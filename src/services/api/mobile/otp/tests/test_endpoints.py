from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from django.test import Client
from django.urls import reverse_lazy

from apps.common.tests.helpers import device_header
from apps.devices.models import Device
from apps.otp.choices import OTPCodeStatus
from apps.otp.models import OTPCode
from apps.otp.tests.factories import OTPCodeFactory

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse
    from django.utils.functional import _StrOrPromise

SEND_URL = reverse_lazy("api:mobile:otp:send")
VERIFY_URL = reverse_lazy("api:mobile:otp:verify")
RESEND_URL = reverse_lazy("api:mobile:otp:resend")

# OTP_DEBUG is on in the test config, so generated codes are always 1111.
DEBUG_CODE = 1111


def _post(
    client: Client,
    url: _StrOrPromise,
    body: dict[str, Any],
    device: Device,
) -> _MonkeyPatchedWSGIResponse:
    return client.post(
        url,
        data=body,
        content_type="application/json",
        headers=device_header(device),
    )


@pytest.mark.django_db
class TestOtpSend:
    def test_send_creates_code_and_returns_token(
        self,
        client: Client,
        device: Device,
    ) -> None:
        response = _post(
            client, SEND_URL, {"email": "user@example.com"}, device
        )

        assert response.status_code == 201
        token = response.json()["otpToken"]
        # Query by the unique token from the response, not the (potentially
        # shared) email, to stay isolated from any leaked rows.
        otp = OTPCode.objects.get(otp_token=token)
        assert otp.email == "user@example.com"
        assert otp.status == OTPCodeStatus.SENT

    def test_send_when_active_code_exists_returns_429(
        self,
        client: Client,
        device: Device,
    ) -> None:
        # An active (recent, SENT) code already exists for this email.
        OTPCodeFactory.create(email="user@example.com")

        response = _post(
            client, SEND_URL, {"email": "user@example.com"}, device
        )

        assert response.status_code == 429

    def test_send_requires_device_header(self, client: Client) -> None:
        response = client.post(
            SEND_URL,
            data={"email": "user@example.com"},
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_send_unknown_device_is_rejected(self, client: Client) -> None:
        # Well-formed but non-existent device id.
        response = client.post(
            SEND_URL,
            data={"email": "user@example.com"},
            content_type="application/json",
            headers={"DEVICE-ID": "00000000-0000-0000-0000-000000000000"},
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestOtpVerify:
    def test_verify_success(
        self,
        client: Client,
        device: Device,
    ) -> None:
        otp = OTPCodeFactory.create(code=DEBUG_CODE)

        response = _post(
            client,
            VERIFY_URL,
            {"otpToken": otp.otp_token, "code": DEBUG_CODE},
            device,
        )

        assert response.status_code == 200
        assert response.json()["verified"] is True
        otp.refresh_from_db()
        assert otp.status == OTPCodeStatus.VERIFIED

    def test_verify_wrong_code(
        self,
        client: Client,
        device: Device,
    ) -> None:
        otp = OTPCodeFactory.create(code=DEBUG_CODE)

        response = _post(
            client,
            VERIFY_URL,
            {"otpToken": otp.otp_token, "code": 9999},
            device,
        )

        assert response.status_code == 400

    def test_verify_unknown_token(
        self,
        client: Client,
        device: Device,
    ) -> None:
        response = _post(
            client,
            VERIFY_URL,
            {"otpToken": "missing", "code": DEBUG_CODE},
            device,
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestOtpResend:
    def test_resend_issues_new_token(
        self,
        client: Client,
        device: Device,
    ) -> None:
        otp = OTPCodeFactory.create(email="user@example.com")

        response = _post(
            client, RESEND_URL, {"otpToken": otp.otp_token}, device
        )

        assert response.status_code == 201
        assert response.json()["otpToken"]
        # Still a single OTP row for this email.
        assert OTPCode.objects.filter(email="user@example.com").count() == 1

    def test_resend_unknown_token(
        self,
        client: Client,
        device: Device,
    ) -> None:
        response = _post(client, RESEND_URL, {"otpToken": "missing"}, device)

        assert response.status_code == 400

    def test_resend_used_token_rejected(
        self,
        client: Client,
        device: Device,
    ) -> None:
        otp = OTPCodeFactory.create(status=OTPCodeStatus.USED)

        response = _post(
            client, RESEND_URL, {"otpToken": otp.otp_token}, device
        )

        assert response.status_code == 400
