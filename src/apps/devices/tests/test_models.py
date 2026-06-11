import pytest

from apps.common.choices import Language
from apps.devices.choices import DeviceOSName
from apps.devices.models import Device


@pytest.mark.django_db
class TestDevice:
    def test_str_returns_device_id(self):
        device = Device.objects.create(
            device_id="device-123",
            os_name=DeviceOSName.IOS,
            app_version="1.0.0",
            os_version="17.0",
            model="iPhone",
        )

        assert str(device) == "device-123"

    def test_language_defaults_to_english(self):
        device = Device.objects.create(
            device_id="device-123",
            os_name=DeviceOSName.ANDROID,
            app_version="1.0.0",
            os_version="14",
            model="Pixel",
        )

        assert device.language == Language.ENGLISH

    def test_id_is_uuid_and_auth_token_optional(self):
        device = Device.objects.create(
            device_id="device-123",
            os_name=DeviceOSName.IOS,
            app_version="1.0.0",
            os_version="17.0",
            model="iPhone",
        )

        assert device.auth_token is None
        # UUID primary key, not an auto-increment integer.
        assert not isinstance(device.pk, int)
