import pytest
from django.test import Client
from django.urls import reverse_lazy

from apps.common.tests.factories import AccessTokenFactory
from apps.common.tests.helpers import AuthContext, bearer, device_header
from apps.devices.tests.factories import DeviceFactory
from apps.users.tests.factories import UserFactory

LIST_URL = reverse_lazy("api:mobile:users:list")


def _staff_auth() -> AuthContext:
    """An authenticated staff member on a token-bound device."""
    token = AccessTokenFactory.create(user=UserFactory.create(is_staff=True))
    device = DeviceFactory.create(auth_token=token)
    return AuthContext(user=token.user, token=token, device=device)


@pytest.mark.django_db
class TestUserListController:
    def test_staff_lists_all_users(self, client: Client) -> None:
        admin = _staff_auth()
        UserFactory.create_batch(2)

        response = client.get(
            LIST_URL,
            headers=bearer(admin.token, admin.device),
        )

        assert response.status_code == 200
        data = response.json()
        # The admin plus the two freshly created users.
        assert len(data) == 3
        assert admin.user.id in {item["id"] for item in data}

    def test_regular_user_is_forbidden(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        response = client.get(
            LIST_URL,
            headers=bearer(auth.token, auth.device),
        )

        assert response.status_code == 403

    def test_requires_authentication(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        response = client.get(LIST_URL, headers=device_header(auth.device))

        assert response.status_code in (401, 403)
