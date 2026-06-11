import pytest
from django.test import Client
from django.urls import reverse_lazy
from oauth2_provider.models import AccessToken, RefreshToken

from apps.common.tests.factories import (
    AccessTokenFactory,
    RefreshTokenFactory,
)
from apps.common.tests.helpers import AuthContext, bearer, device_header
from apps.devices.tests.factories import DeviceFactory

ME_URL = reverse_lazy("api:mobile:users:me")


@pytest.mark.django_db
class TestUserMeController:
    def test_me_allows_token_bound_to_device(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        response = client.get(ME_URL, headers=bearer(auth.token, auth.device))

        assert response.status_code == 200
        assert response.json()["email"] == auth.user.email

    def test_me_requires_authentication(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        response = client.get(ME_URL, headers=device_header(auth.device))

        assert response.status_code in (401, 403)

    def test_me_updates_profile(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        response = client.patch(
            ME_URL,
            data={"firstName": "New", "lastName": "Profile"},
            content_type="application/json",
            headers=bearer(auth.token, auth.device),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["firstName"] == "New"
        assert data["lastName"] == "Profile"
        auth.user.refresh_from_db()
        assert auth.user.first_name == "New"
        assert auth.user.last_name == "Profile"

    def test_me_rejects_device_bound_to_another_token(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        # A second device bound to a different user's token.
        other_token = AccessTokenFactory.create()
        other_device = DeviceFactory.create(auth_token=other_token)

        response = client.get(
            ME_URL,
            headers=bearer(auth.token, other_device),
        )

        assert response.status_code == 403

    def test_me_soft_deletes_user_and_revokes_all_tokens(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        # A second active session for the same user.
        RefreshTokenFactory.create(access_token=auth.token)
        second_token = AccessTokenFactory.create(
            user=auth.user,
            application=auth.token.application,
        )
        RefreshTokenFactory.create(access_token=second_token)
        DeviceFactory.create(auth_token=second_token)

        response = client.delete(
            ME_URL,
            headers=bearer(auth.token, auth.device),
        )

        assert response.status_code == 204
        auth.user.refresh_from_db()
        assert not auth.user.is_active
        # Every token pair for the user is revoked, not just the current one.
        assert not AccessToken.objects.filter(user_id=auth.user.id).exists()
        assert not RefreshToken.objects.filter(
            user_id=auth.user.id, revoked__isnull=True
        ).exists()

    def test_me_rejects_inactive_user(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        auth.user.is_active = False
        auth.user.save(update_fields=["is_active"])

        response = client.get(ME_URL, headers=bearer(auth.token, auth.device))

        assert response.status_code == 403
