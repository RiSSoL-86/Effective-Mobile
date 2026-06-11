import factory
from factory.django import DjangoModelFactory

from apps.common.choices import Language
from apps.devices.choices import DeviceOSName
from apps.devices.models import Device


class DeviceFactory(DjangoModelFactory[Device]):
    class Meta:
        model = Device

    device_id = factory.Sequence(lambda n: f"device-{n}")
    os_name = DeviceOSName.IOS
    app_version = "1.0.0"
    os_version = "17.0"
    model = "iPhone"
    language = Language.ENGLISH
    auth_token = None
