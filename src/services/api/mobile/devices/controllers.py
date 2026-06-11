from http import HTTPStatus
from typing import final

from dmr import Body, Controller, Headers, modify
from dmr.plugins.pydantic import PydanticSerializer

from services.api.mobile.devices.schemas import (
    DeviceInitHeaders,
    DeviceInitRequest,
    DeviceResponse,
)
from services.api.mobile.devices.services.init import DeviceInitService


@final
class DeviceInitController(Controller[PydanticSerializer]):
    @modify(status_code=HTTPStatus.CREATED, tags=["Devices"])
    async def post(
        self,
        parsed_body: Body[DeviceInitRequest],
        parsed_headers: Headers[DeviceInitHeaders],
    ) -> DeviceResponse:
        service = DeviceInitService()
        device = await service.execute(
            parsed_body,
            device_id=parsed_headers.device_id,
            firebase_token=parsed_headers.firebase_token,
        )
        return DeviceResponse.model_validate(device)
