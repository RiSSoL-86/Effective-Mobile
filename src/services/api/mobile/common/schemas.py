from uuid import UUID

from pydantic import Field

from services.api.common.schemas import CamelCaseModel


class DeviceIdHeaders(CamelCaseModel):
    device_id: UUID = Field(alias="DEVICE-ID")
