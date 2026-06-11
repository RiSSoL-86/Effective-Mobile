from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from django.test import Client
from django.urls import reverse_lazy
from oauth2_provider.models import AccessToken, Application, RefreshToken

from apps.common.tests.factories import (
    ApplicationFactory,
    RefreshTokenFactory,
)
from apps.common.tests.helpers import AuthContext, bearer, device_header
from apps.devices.models import Device
from apps.devices.tests.factories import DeviceFactory
from apps.otp.choices import OTPCodeStatus
from apps.otp.models import OTPCode
from apps.otp.tests.factories import OTPCodeFactory
from apps.users.models import User
from apps.users.tests.factories import DEFAULT_PASSWORD, UserFactory

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse

SIGNUP_URL = reverse_lazy("api:mobile:auth:signup")
SIGNIN_URL = reverse_lazy("api:mobile:auth:signin")
REFRESH_URL = reverse_lazy("api:mobile:auth:refresh")
LOGOUT_URL = reverse_lazy("api:mobile:auth:logout")


def _client_headers(
    application: Application,
    device: Device,
) -> dict[str, str]:
    """DEVICE-ID + CLIENT-ID headers required by signup/signin."""
    return {
        "DEVICE-ID": str(device.id),
        "CLIENT-ID": application.client_id,
    }


@pytest.mark.django_db
class TestSignup:
    def _payload(self, **overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "otpToken": "otp-token",
            "firstName": "John",
            "lastName": "Doe",
            "password": "secret-pass",
            "passwordRepeat": "secret-pass",
        }
        payload.update(overrides)
        return payload

    def _post(
        self,
        client: Client,
        body: dict[str, Any],
        application: Application,
        device: Device,
    ) -> _MonkeyPatchedWSGIResponse:
        return client.post(
            SIGNUP_URL,
            data=body,
            content_type="application/json",
            headers=_client_headers(application, device),
        )

    def test_signup_creates_user_and_tokens(self, client: Client) -> None:
        application = ApplicationFactory.create()
        device = DeviceFactory.create()
        OTPCodeFactory.create(
            email="new@example.com",
            otp_token="otp-token",
            status=OTPCodeStatus.VERIFIED,
        )

        response = self._post(client, self._payload(), application, device)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["accessToken"]
        assert data["refreshToken"]

        user = User.objects.get(email="new@example.com")
        assert user.first_name == "John"
        # OTP consumed, token bound to the device.
        otp = OTPCode.objects.get(otp_token="otp-token")
        assert otp.status == OTPCodeStatus.USED
        device.refresh_from_db()
        assert device.auth_token_id is not None

    def test_signup_password_mismatch(self, client: Client) -> None:
        application = ApplicationFactory.create()
        device = DeviceFactory.create()

        response = self._post(
            client,
            self._payload(passwordRepeat="different"),
            application,
            device,
        )

        assert response.status_code == 400

    def test_signup_existing_user_conflict(self, client: Client) -> None:
        application = ApplicationFactory.create()
        device = DeviceFactory.create()
        UserFactory.create(email="new@example.com")
        OTPCodeFactory.create(
            email="new@example.com",
            otp_token="otp-token",
            status=OTPCodeStatus.VERIFIED,
        )

        response = self._post(client, self._payload(), application, device)

        assert response.status_code == 409


@pytest.mark.django_db
class TestSignin:
    def _post(
        self,
        client: Client,
        body: dict[str, Any],
        application: Application,
        device: Device,
    ) -> _MonkeyPatchedWSGIResponse:
        return client.post(
            SIGNIN_URL,
            data=body,
            content_type="application/json",
            headers=_client_headers(application, device),
        )

    def test_signin_success(self, client: Client) -> None:
        application = ApplicationFactory.create()
        device = DeviceFactory.create()
        user = UserFactory.create()

        response = self._post(
            client,
            {"email": user.email, "password": DEFAULT_PASSWORD},
            application,
            device,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert data["accessToken"]
        device.refresh_from_db()
        assert device.auth_token_id is not None

    def test_signin_wrong_password(self, client: Client) -> None:
        application = ApplicationFactory.create()
        device = DeviceFactory.create()
        user = UserFactory.create()

        response = self._post(
            client,
            {"email": user.email, "password": "wrong"},
            application,
            device,
        )

        assert response.status_code == 401

    def test_signin_inactive_user(self, client: Client) -> None:
        application = ApplicationFactory.create()
        device = DeviceFactory.create()
        user = UserFactory.create(is_active=False)

        response = self._post(
            client,
            {"email": user.email, "password": DEFAULT_PASSWORD},
            application,
            device,
        )

        assert response.status_code == 403

    def test_signin_unknown_client_id(self, client: Client) -> None:
        device = DeviceFactory.create()
        user = UserFactory.create()

        # Valid credentials but a bogus CLIENT-ID.
        response = client.post(
            SIGNIN_URL,
            data={"email": user.email, "password": DEFAULT_PASSWORD},
            content_type="application/json",
            headers={
                "DEVICE-ID": str(device.id),
                "CLIENT-ID": "does-not-exist",
            },
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestRefresh:
    def test_refresh_rotates_tokens(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        refresh = RefreshTokenFactory.create(access_token=auth.token)

        response = client.post(
            REFRESH_URL,
            data={"refreshToken": refresh.token},
            content_type="application/json",
            headers=device_header(auth.device),
        )

        assert response.status_code == 201
        data = response.json()
        assert data["accessToken"] != auth.token.token
        # A fresh, usable refresh token is issued...
        new_refresh = data["refreshToken"]
        assert new_refresh != refresh.token
        assert RefreshToken.objects.filter(
            token=new_refresh, revoked__isnull=True
        ).exists()
        # ...and the old refresh token can no longer be used.
        assert not RefreshToken.objects.filter(
            token=refresh.token, revoked__isnull=True
        ).exists()

    def test_refresh_invalid_token(
        self,
        client: Client,
        device: Device,
    ) -> None:
        response = client.post(
            REFRESH_URL,
            data={"refreshToken": "nope"},
            content_type="application/json",
            headers=device_header(device),
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestLogout:
    def test_logout_revokes_current_token_pair(
        self,
        client: Client,
        auth: AuthContext,
    ) -> None:
        refresh = RefreshTokenFactory.create(access_token=auth.token)

        response = client.post(
            LOGOUT_URL,
            headers=bearer(auth.token, auth.device),
        )

        assert response.status_code == 204
        assert not AccessToken.objects.filter(pk=auth.token.pk).exists()
        assert not RefreshToken.objects.filter(pk=refresh.pk).exists()
        auth.device.refresh_from_db()
        assert auth.device.auth_token_id is None

    def test_logout_requires_authentication(
        self,
        client: Client,
        device: Device,
    ) -> None:
        # No Bearer token supplied.
        response = client.post(LOGOUT_URL, headers=device_header(device))

        assert response.status_code in (401, 403)
