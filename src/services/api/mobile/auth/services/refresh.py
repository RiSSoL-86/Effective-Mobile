from datetime import timedelta
from typing import final, override

from django.utils import timezone
from oauth2_provider.models import RefreshToken
from oauth2_provider.settings import oauth2_settings

from apps.devices.models import Device
from apps.users.services import (
    bind_access_token_to_device,
    create_oauth_tokens,
)
from services.api.mobile.auth.exceptions import (
    InvalidRefreshTokenError,
    RefreshTokenExpiredError,
)
from services.api.mobile.auth.schemas import RefreshRequest
from services.api.mobile.common.service import BaseService


@final
class RefreshService(BaseService):
    @override
    async def execute(
        self,
        payload: RefreshRequest,
        device: Device,
    ) -> dict[str, str]:
        try:
            old_refresh_token = await RefreshToken.objects.select_related(
                "user",
                "application",
            ).aget(
                token=payload.refresh_token,
                revoked__isnull=True,
            )
        except RefreshToken.DoesNotExist as err:
            raise InvalidRefreshTokenError() from err

        refresh_expires_at = old_refresh_token.created + timedelta(
            seconds=oauth2_settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )
        if refresh_expires_at < timezone.now():
            raise RefreshTokenExpiredError()

        access_token, new_refresh_token = await create_oauth_tokens(
            old_refresh_token.user,
            old_refresh_token.application,
        )
        old_refresh_token.revoked = timezone.now()
        await old_refresh_token.asave(update_fields=["revoked"])
        await bind_access_token_to_device(
            access_token=access_token,
            device=device,
        )
        return {
            "email": old_refresh_token.user.email,
            "access_token": access_token.token,
            "refresh_token": new_refresh_token.token,
        }
