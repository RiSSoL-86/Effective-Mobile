from http import HTTPStatus

from dmr import Controller, ResponseSpec
from dmr.plugins.pydantic import PydanticSerializer

from apps.devices.models import Device
from services.api.common.controllers import AuthenticatedController
from services.api.mobile.common.exceptions import DeviceTokenMismatchError
from services.api.mobile.common.mixins import DeviceHeaderMixin
from services.api.mobile.common.schemas import DeviceIdHeaders


class MobileController(DeviceHeaderMixin, Controller[PydanticSerializer]):
    pass


class MobileAuthenticatedController(
    DeviceHeaderMixin, AuthenticatedController
):
    responses = [
        ResponseSpec(
            AuthenticatedController.error_model,
            status_code=HTTPStatus.FORBIDDEN,
        ),
    ]

    async def set_device(self, parsed_headers: DeviceIdHeaders) -> Device:
        device = await super().set_device(parsed_headers)
        if device.auth_token_id != self.token.id:
            raise DeviceTokenMismatchError()
        return device
