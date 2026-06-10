from typing import TYPE_CHECKING, final, override

from apps.devices.models import Device
from services.api.mobile.common.service import BaseService

if TYPE_CHECKING:
    from services.api.mobile.devices.schemas import DeviceInitRequest


@final
class DeviceInitService(BaseService):
    @override
    async def execute(
        self,
        payload: "DeviceInitRequest",
        device_id: str,
        firebase_token: str,
    ) -> Device:
        data = {
            **payload.model_dump(),
            "device_id": device_id,
            "firebase_token": firebase_token,
        }
        device, _ = await Device.objects.aupdate_or_create(
            device_id=device_id,
            defaults=data,
        )
        return device
