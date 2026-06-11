from uuid import UUID

from pydantic import Field, field_serializer

from apps.common.choices import Language
from apps.devices.choices import DeviceOSName
from services.api.common.schemas import CamelCaseModel


class DeviceInitRequest(CamelCaseModel):
    os_name: DeviceOSName
    app_version: str = Field(..., max_length=200)
    os_version: str = Field(..., max_length=200)
    model: str = Field(..., max_length=200)
    language: Language = Language.RUSSIAN


class DeviceInitHeaders(CamelCaseModel):
    device_id: str = Field(alias="X-DEVICE-ID", max_length=200)
    firebase_token: str = Field(alias="FIREBASE-TOKEN", max_length=255)


class DeviceResponse(CamelCaseModel):
    id: UUID
    os_name: DeviceOSName
    app_version: str = Field(..., max_length=200)
    os_version: str = Field(..., max_length=200)
    model: str = Field(..., max_length=200)
    language: Language

    @field_serializer("os_name", return_type=str)
    def serialize_os_name(self, os_name: DeviceOSName) -> str:
        return str(os_name.label)

    @field_serializer("language", return_type=str)
    def serialize_language(self, language: Language) -> str:
        return str(language.label)
