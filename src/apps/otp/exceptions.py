from http import HTTPStatus

from django.utils.translation import gettext_lazy as _

from apps.common.exceptions import CustomMessageException


class InvalidCodeError(CustomMessageException):
    custom_message = _("invalid code")
    field = "code"


class OTPThrottledError(CustomMessageException):
    custom_message = _(
        "The code has already been sent, please try again later"
    )
    field = "email"
    status_code = HTTPStatus.TOO_MANY_REQUESTS


class OTPExpiredError(CustomMessageException):
    custom_message = _("code expired")
    field = "otp_token"


class OTPStatusError(CustomMessageException):
    custom_message = _("code has already been used, please request a new one")
    field = "otp_token"


class InvalidTokenError(CustomMessageException):
    custom_message = _("invalid otp_token")
    field = "otp_token"
