from http import HTTPStatus

from django.utils.translation import gettext_lazy as _

from apps.common.exceptions import CustomMessageException


class InvalidClientIDError(CustomMessageException):
    custom_message = _("Invalid CLIENT-ID.")
    loc = ["headers", "CLIENT-ID"]


class MismatchUserPasswordFieldsError(CustomMessageException):
    custom_message = _("password and password_repeat do not match.")
    loc = ["password", "password_repeat"]


class UserAlreadyExistsError(CustomMessageException):
    custom_message = _(
        "An account with this email already exists, please sign in."
    )
    loc = ["otpToken"]
    status_code = HTTPStatus.CONFLICT


class InvalidCredentialsError(CustomMessageException):
    custom_message = _("Invalid email or password.")
    loc = ["email", "password"]
    status_code = HTTPStatus.UNAUTHORIZED


class InvalidRefreshTokenError(CustomMessageException):
    custom_message = _("Invalid refreshToken.")
    field = "refresh_token"


class RefreshTokenExpiredError(CustomMessageException):
    custom_message = _("refreshToken expired, please login again.")
    field = "refresh_token"
