from http import HTTPStatus

from django.utils.translation import gettext_lazy as _

from apps.common.exceptions import CustomMessageException


class UserInactiveError(CustomMessageException):
    custom_message = _("User is blocked")
    field = "user"
    status_code = HTTPStatus.FORBIDDEN


class UserAccessDeniedError(CustomMessageException):
    custom_message = _("You do not have permission to access this user")
    field = "user"
    status_code = HTTPStatus.FORBIDDEN


class UserNotFoundError(CustomMessageException):
    custom_message = _("User not found")
    field = "user"
    status_code = HTTPStatus.NOT_FOUND
