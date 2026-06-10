"""Helpers shared by API tests: auth context and request-header builders."""

from __future__ import annotations

from typing import NamedTuple

from oauth2_provider.models import AccessToken

from apps.devices.models import Device
from apps.users.models import User


class AuthContext(NamedTuple):
    """A user authenticated on a device, with a bound access token."""

    user: User
    token: AccessToken
    device: Device


def bearer(token: AccessToken, device: Device) -> dict[str, str]:
    """Headers authenticating ``token`` for requests from ``device``."""
    return {
        "Authorization": f"Bearer {token.token}",
        "DEVICE-ID": str(device.id),
    }


def device_header(device: Device) -> dict[str, str]:
    """The ``DEVICE-ID`` header for unauthenticated mobile endpoints."""
    return {"DEVICE-ID": str(device.id)}
