from http import HTTPStatus

from django.utils.translation import gettext_lazy as _

from apps.common.exceptions import CustomMessageException


class InvalidDeviceIDError(CustomMessageException):
    custom_message = _("Invalid DEVICE-ID.")
    loc = ["headers", "DEVICE-ID"]


class DeviceTokenMismatchError(CustomMessageException):
    custom_message = _("DEVICE-ID does not match the access token.")
    loc = ["headers", "DEVICE-ID"]
    status_code = HTTPStatus.FORBIDDEN
