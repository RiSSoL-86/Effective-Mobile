"""Shared pytest fixtures for the API test suite.

Imports of Django models are kept inside the fixture bodies so the conftest
can be loaded before the app registry is ready.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from apps.common.tests.helpers import AuthContext
    from apps.devices.models import Device


@pytest.fixture
def device(db: None) -> Device:
    """An initialised device without any bound token."""
    from apps.devices.tests.factories import DeviceFactory

    return DeviceFactory.create()


@pytest.fixture
def auth(db: None) -> AuthContext:
    """A device whose bound access token authenticates its owner."""
    from apps.common.tests.factories import AccessTokenFactory
    from apps.common.tests.helpers import AuthContext
    from apps.devices.tests.factories import DeviceFactory

    token = AccessTokenFactory.create()
    bound_device = DeviceFactory.create(auth_token=token)
    return AuthContext(
        user=token.user,
        token=token,
        device=bound_device,
    )
