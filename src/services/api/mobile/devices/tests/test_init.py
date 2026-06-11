from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from django.test import Client
from django.urls import reverse_lazy

from apps.devices.choices import DeviceOSName
from apps.devices.models import Device

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse

URL = reverse_lazy("api:mobile:devices:init")


def _post(
    client: Client,
    body: dict[str, Any],
    device_id: str = "device-1",
) -> _MonkeyPatchedWSGIResponse:
    return client.post(
        URL,
        data=body,
        content_type="application/json",
        headers={
            "X-DEVICE-ID": device_id,
            "FIREBASE-TOKEN": "firebase-token",
        },
    )


@pytest.mark.django_db
class TestDeviceInitController:
    payload: dict[str, Any] = {
        "osName": DeviceOSName.IOS.value,
        "appVersion": "1.0.0",
        "osVersion": "17.0",
        "model": "iPhone 15",
        "language": 0,
    }

    def test_init_creates_device(self, client: Client) -> None:
        # Act
        response = _post(client, self.payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["appVersion"] == "1.0.0"
        assert data["model"] == "iPhone 15"
        # os_name / language serialized to human-readable labels
        assert data["osName"] == "ios"
        assert data["language"] == "russian"

        device = Device.objects.get(device_id="device-1")
        assert device.firebase_token == "firebase-token"
        assert str(device.id) == data["id"]

    def test_init_is_idempotent_per_device_id(self, client: Client) -> None:
        # Arrange - first init
        _post(client, self.payload)

        # Act - second init with same X-DEVICE-ID but new data
        updated = dict(self.payload, model="iPhone 16", appVersion="2.0.0")
        response = _post(client, updated)

        # Assert - updated in place, not duplicated
        assert response.status_code == 201
        assert Device.objects.filter(device_id="device-1").count() == 1
        device = Device.objects.get(device_id="device-1")
        assert device.model == "iPhone 16"
        assert device.app_version == "2.0.0"

    def test_init_requires_device_headers(self, client: Client) -> None:
        # Act - missing X-DEVICE-ID / FIREBASE-TOKEN headers
        response = client.post(
            URL,
            data=self.payload,
            content_type="application/json",
        )

        # Assert
        assert response.status_code == 400

    def test_init_rejects_invalid_os_name(self, client: Client) -> None:
        # Act
        response = _post(client, dict(self.payload, osName=99))

        # Assert
        assert response.status_code == 400
