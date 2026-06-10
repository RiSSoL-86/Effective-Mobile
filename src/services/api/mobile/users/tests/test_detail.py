import pytest
from django.test import Client
from django.urls import reverse

from apps.common.tests.factories import AccessTokenFactory
from apps.common.tests.helpers import AuthContext, bearer, device_header
from apps.devices.tests.factories import DeviceFactory
from apps.users.tests.factories import UserFactory


def _detail_url(user_id: int) -> str:
    return reverse("api:mobile:users:detail", kwargs={"user_id": user_id})


def _staff_auth() -> AuthContext:
    """An authenticated staff member on a token-bound device."""
    token = AccessTokenFactory.create(user=UserFactory.create(is_staff=True))
    device = DeviceFactory.create(auth_token=token)
    return AuthContext(user=token.user, token=token, device=device)


@pytest.mark.django_db
class TestUserDetailController:
    def test_user_can_fetch_themselves(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        response = client.get(
            _detail_url(auth.user.id),
            headers=bearer(auth.token, auth.device),
        )

        assert response.status_code == 200
        assert response.json()["id"] == auth.user.id
        assert response.json()["email"] == auth.user.email

    def test_user_cannot_fetch_another_user(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        other = UserFactory.create()

        response = client.get(
            _detail_url(other.id),
            headers=bearer(auth.token, auth.device),
        )

        assert response.status_code == 403

    def test_staff_can_fetch_any_user(self, client: Client) -> None:
        admin = _staff_auth()
        other = UserFactory.create()

        response = client.get(
            _detail_url(other.id),
            headers=bearer(admin.token, admin.device),
        )

        assert response.status_code == 200
        assert response.json()["id"] == other.id

    def test_staff_gets_404_for_missing_user(self, client: Client) -> None:
        admin = _staff_auth()

        response = client.get(
            _detail_url(999999),
            headers=bearer(admin.token, admin.device),
        )

        assert response.status_code == 404

    def test_requires_authentication(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        response = client.get(
            _detail_url(auth.user.id),
            headers=device_header(auth.device),
        )

        assert response.status_code in (401, 403)
