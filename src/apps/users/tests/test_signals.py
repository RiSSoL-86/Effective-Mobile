import pytest

from apps.common.tests.factories import AccessTokenFactory
from apps.devices.models import Device
from apps.devices.tests.factories import DeviceFactory


@pytest.mark.django_db
class TestDeleteUserDevicesSignal:
    def test_deleting_user_deletes_their_devices(self):
        # Arrange
        token = AccessTokenFactory.create()
        device = DeviceFactory.create(auth_token=token)

        # Act
        token.user.delete()

        # Assert
        assert not Device.objects.filter(pk=device.pk).exists()

    def test_deleting_user_keeps_other_users_devices(self):
        # Arrange
        target = DeviceFactory.create(auth_token=AccessTokenFactory.create())
        other = DeviceFactory.create(auth_token=AccessTokenFactory.create())

        # Act
        target.auth_token.user.delete()

        # Assert
        assert not Device.objects.filter(pk=target.pk).exists()
        assert Device.objects.filter(pk=other.pk).exists()
