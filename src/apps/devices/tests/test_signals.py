import pytest
from oauth2_provider.models import AccessToken, RefreshToken

from apps.common.tests.factories import (
    AccessTokenFactory,
    ApplicationFactory,
)
from apps.devices.tests.factories import DeviceFactory
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestDeleteOldTokensSignal:
    def test_binding_token_to_device_deletes_orphan_tokens(self):
        # Arrange - same user/app, but tokens not attached to any device
        user = UserFactory.create()
        application = ApplicationFactory.create()
        orphan_access = AccessTokenFactory.create(
            user=user, application=application
        )
        orphan_refresh = RefreshToken.objects.create(
            user=user,
            application=application,
            token="orphan-refresh",
            access_token=None,
        )
        new_token = AccessTokenFactory.create(
            user=user, application=application
        )

        # Act - saving a device bound to new_token triggers the signal
        DeviceFactory.create(auth_token=new_token)

        # Assert - orphaned (deviceless / access-less) tokens are purged
        assert not AccessToken.objects.filter(pk=orphan_access.pk).exists()
        assert not RefreshToken.objects.filter(pk=orphan_refresh.pk).exists()
        # The token bound to the new device survives.
        assert AccessToken.objects.filter(pk=new_token.pk).exists()

    def test_device_without_token_is_noop(self):
        # Arrange
        orphan_access = AccessTokenFactory.create()

        # Act - device with no auth_token must not crash or purge anything
        DeviceFactory.create(auth_token=None)

        # Assert
        assert AccessToken.objects.filter(pk=orphan_access.pk).exists()
