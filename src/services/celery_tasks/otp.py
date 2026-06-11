from celery import shared_task


@shared_task(name="otp.send_code_task")
def send_code_task(code: int, email: str) -> None:
    from apps.otp.services import send_code

    send_code(code=code, email=email)
