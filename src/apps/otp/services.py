import random
import secrets
from datetime import timedelta
from email.mime.image import MIMEImage
from pathlib import Path

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone

from apps.otp.choices import OTPCodeStatus
from apps.otp.exceptions import (
    InvalidCodeError,
    InvalidTokenError,
    OTPExpiredError,
    OTPStatusError,
)
from apps.otp.models import OTPCode
from services.celery_tasks.otp import send_code_task


def send_code(code: int, email: str) -> None:
    context = {"code": code, "domain": settings.DOMAIN_NAME}  # type: ignore

    subject_template = get_template("otp/send_code/subject.txt")
    subject = subject_template.render(context)

    txt_template = get_template("otp/send_code/txt_content.txt")
    txt_body = txt_template.render(context)

    html_template = get_template("otp/send_code/email-confirmation-code.html")
    html_body = html_template.render(context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=txt_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    msg.attach_alternative(content=html_body, mimetype="text/html")

    dir = Path(settings.BASE_DIR)
    images = {
        "logo": dir / "static" / "images" / "mail_logo.png",
        "name": dir / "static" / "images" / "name.png",
    }

    for cid, path in images.items():
        with open(path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", f"<{cid}>")
            img.add_header("Content-Disposition", "inline", filename=path.name)
            msg.attach(img)

    msg.send()


def should_use_test_otp(email: str) -> bool:
    if settings.OTP_DEBUG:  # type: ignore
        return True
    if email.lower() in settings.OTP_TEST_EMAILS_SET:  # type: ignore
        return True
    return False


def resolve_otp_code_for_email(email: str, length: int = 6) -> int:
    if should_use_test_otp(email):
        return settings.OTP_DEBUG_CODE  # type: ignore
    return generate_code(length)


def generate_code(length: int = 6) -> int:
    min_value = 10 ** (length - 1)
    max_value = 10**length - 1
    return random.randrange(min_value, max_value)


def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)[:length]


async def create_otp_code(email: str) -> OTPCode:
    otp_code = await OTPCode.objects.acreate(
        email=email,
        status=OTPCodeStatus.SENT,
        otp_token=generate_token(),
        code=resolve_otp_code_for_email(email, length=4),
    )
    return otp_code


async def update_or_create_otp_code(email: str) -> OTPCode:
    otp_code, _ = await OTPCode.objects.aupdate_or_create(
        email=email,
        defaults={
            "status": OTPCodeStatus.SENT,
            "otp_token": generate_token(),
            "code": resolve_otp_code_for_email(email, length=4),
        },
    )
    return otp_code


async def send_code_task_delay(code: int, email: str) -> None:
    if should_use_test_otp(email):
        return
    await sync_to_async(send_code_task.delay)(code=code, email=email)


async def has_active_otp_code(email: str) -> tuple[bool, OTPCode | None]:
    lifetime = timezone.now() - timedelta(minutes=settings.OTP_CODE_LIFETIME)  # type: ignore
    try:
        otp = await OTPCode.objects.aget(
            email=email,
            status=OTPCodeStatus.SENT,
            updated_timestamp__gte=lifetime,
        )
        return True, otp
    except OTPCode.DoesNotExist:
        return False, None


async def verify_otp(otp_token: str, code: int) -> None:
    otp_code = await OTPCode.objects.filter(otp_token=otp_token).afirst()
    if not otp_code:
        raise InvalidTokenError()
    if otp_code.code != code:
        raise InvalidCodeError()
    if otp_code.status != OTPCodeStatus.SENT:
        raise OTPStatusError()
    lifetime = timedelta(minutes=settings.OTP_CODE_LIFETIME)  # type: ignore
    if otp_code.updated_timestamp < timezone.now() - lifetime:
        raise OTPExpiredError()
    otp_code.status = OTPCodeStatus.VERIFIED
    await otp_code.asave(update_fields=["status", "updated_timestamp"])


async def get_verified_otp(otp_token: str) -> OTPCode:
    try:
        otp = await OTPCode.objects.aget(otp_token=otp_token)
    except OTPCode.DoesNotExist as err:
        raise InvalidTokenError() from err
    if otp.status != OTPCodeStatus.VERIFIED:
        raise OTPStatusError()
    lifetime = timedelta(minutes=settings.OTP_CODE_LIFETIME)  # type: ignore
    if otp.updated_timestamp < timezone.now() - lifetime:
        raise OTPExpiredError()
    return otp


async def mark_as_used(otp: OTPCode) -> None:
    otp.status = OTPCodeStatus.USED
    await otp.asave(update_fields=["status", "updated_timestamp"])
