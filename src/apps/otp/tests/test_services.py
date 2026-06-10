from datetime import timedelta

import pytest
from asgiref.sync import async_to_sync
from django.test import override_settings
from django.utils import timezone

from apps.otp import services
from apps.otp.choices import OTPCodeStatus
from apps.otp.exceptions import (
    InvalidCodeError,
    InvalidTokenError,
    OTPExpiredError,
    OTPStatusError,
)
from apps.otp.models import OTPCode
from apps.otp.tests.factories import OTPCodeFactory

# These suites run with ``transaction=True`` because the services use the
# async ORM (via ``async_to_sync``), which commits on a separate connection.
# That connection bypasses the test's rollback, so rows committed by async
# endpoints elsewhere can leak. To stay immune, each test creates its own row
# via the factory (unique ``otp_token``/``email`` per ``Sequence``) and only
# ever queries by that instance's own values — never a shared literal.


def _make_otp(
    code: int = 1111,
    status: int = OTPCodeStatus.SENT,
) -> OTPCode:
    """Create an OTP with a factory-unique token and email."""
    return OTPCodeFactory.create(code=code, status=status)


def _age_otp(otp: OTPCode, minutes: int) -> None:
    """Backdate ``updated_timestamp`` bypassing ``auto_now``."""
    old = timezone.now() - timedelta(minutes=minutes)
    OTPCode.objects.filter(pk=otp.pk).update(updated_timestamp=old)


class TestPureHelpers:
    """Functions that do not touch the database."""

    @pytest.mark.parametrize("length", [4, 6, 8])
    def test_generate_code_has_requested_length(self, length):
        code = services.generate_code(length)
        assert len(str(code)) == length

    def test_generate_token_length_capped(self):
        token = services.generate_token(32)
        assert isinstance(token, str)
        assert len(token) == 32

    @override_settings(OTP_DEBUG=True)
    def test_should_use_test_otp_when_debug(self):
        assert services.should_use_test_otp("anything@example.com") is True

    @override_settings(
        OTP_DEBUG=False,
        OTP_TEST_EMAILS_SET=frozenset({"qa@example.com"}),
    )
    def test_should_use_test_otp_for_whitelisted_email(self):
        assert services.should_use_test_otp("QA@example.com") is True
        assert services.should_use_test_otp("real@example.com") is False

    @override_settings(OTP_DEBUG=True, OTP_DEBUG_CODE=1111)
    def test_resolve_otp_code_returns_debug_code(self):
        assert services.resolve_otp_code_for_email("user@example.com") == 1111


@pytest.mark.django_db(transaction=True)
class TestCreateOtpCode:
    def test_create_otp_code_uses_debug_code(self):
        otp = async_to_sync(services.create_otp_code)("create-otp@test.dev")

        assert otp.status == OTPCodeStatus.SENT
        assert otp.code == 1111
        assert otp.otp_token

    def test_update_or_create_refreshes_existing(self):
        email = "update-otp@test.dev"
        first = async_to_sync(services.update_or_create_otp_code)(email)
        first.status = OTPCodeStatus.USED
        first.save(update_fields=["status"])

        second = async_to_sync(services.update_or_create_otp_code)(email)

        # Same row reused (single OTP per email), status reset to SENT.
        assert OTPCode.objects.filter(email=email).count() == 1
        assert second.pk == first.pk
        assert second.status == OTPCodeStatus.SENT


@pytest.mark.django_db(transaction=True)
class TestHasActiveOtpCode:
    def test_returns_true_for_recent_sent_code(self):
        otp = _make_otp()

        active, found = async_to_sync(services.has_active_otp_code)(otp.email)

        assert active is True
        assert found is not None

    def test_returns_false_when_no_code(self):
        active, found = async_to_sync(services.has_active_otp_code)(
            "no-active-code@test.dev",
        )

        assert active is False
        assert found is None

    def test_returns_false_for_expired_code(self):
        otp = _make_otp()
        _age_otp(otp, minutes=20)  # OTP_CODE_LIFETIME is 15

        active, found = async_to_sync(services.has_active_otp_code)(otp.email)

        assert active is False
        assert found is None


@pytest.mark.django_db(transaction=True)
class TestVerifyOtp:
    def test_verify_marks_code_as_verified(self):
        otp = _make_otp(code=1111)

        async_to_sync(services.verify_otp)(otp.otp_token, 1111)

        otp.refresh_from_db()
        assert otp.status == OTPCodeStatus.VERIFIED

    def test_invalid_token_raises(self):
        with pytest.raises(InvalidTokenError):
            async_to_sync(services.verify_otp)("missing-token", 1111)

    def test_wrong_code_raises(self):
        otp = _make_otp(code=1111)

        with pytest.raises(InvalidCodeError):
            async_to_sync(services.verify_otp)(otp.otp_token, 2222)

    def test_non_sent_status_raises(self):
        otp = _make_otp(code=1111, status=OTPCodeStatus.USED)

        with pytest.raises(OTPStatusError):
            async_to_sync(services.verify_otp)(otp.otp_token, 1111)

    def test_expired_code_raises(self):
        otp = _make_otp(code=1111)
        _age_otp(otp, minutes=20)

        with pytest.raises(OTPExpiredError):
            async_to_sync(services.verify_otp)(otp.otp_token, 1111)


@pytest.mark.django_db(transaction=True)
class TestGetVerifiedOtp:
    def test_returns_verified_otp(self):
        otp = _make_otp(status=OTPCodeStatus.VERIFIED)

        found = async_to_sync(services.get_verified_otp)(otp.otp_token)

        assert found.pk == otp.pk

    def test_unknown_token_raises(self):
        with pytest.raises(InvalidTokenError):
            async_to_sync(services.get_verified_otp)("missing-token")

    def test_unverified_status_raises(self):
        otp = _make_otp(status=OTPCodeStatus.SENT)

        with pytest.raises(OTPStatusError):
            async_to_sync(services.get_verified_otp)(otp.otp_token)

    def test_expired_verified_otp_raises(self):
        otp = _make_otp(status=OTPCodeStatus.VERIFIED)
        _age_otp(otp, minutes=20)

        with pytest.raises(OTPExpiredError):
            async_to_sync(services.get_verified_otp)(otp.otp_token)


@pytest.mark.django_db(transaction=True)
class TestMarkAsUsed:
    def test_mark_as_used(self):
        otp = _make_otp(status=OTPCodeStatus.VERIFIED)

        async_to_sync(services.mark_as_used)(otp)

        otp.refresh_from_db()
        assert otp.status == OTPCodeStatus.USED
