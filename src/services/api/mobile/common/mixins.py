from apps.devices.models import Device
from services.api.mobile.common.exceptions import InvalidDeviceIDError
from services.api.mobile.common.schemas import DeviceIdHeaders


class DeviceHeaderMixin:
    async def set_device(self, parsed_headers: DeviceIdHeaders) -> Device:
        device = await Device.objects.filter(
            id=parsed_headers.device_id,
        ).afirst()
        if device is None:
            raise InvalidDeviceIDError()

        self.request.device = device  # type: ignore
        return device
