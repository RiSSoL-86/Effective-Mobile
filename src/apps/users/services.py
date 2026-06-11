from datetime import timedelta

from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauth2_provider.settings import oauth2_settings
from oauthlib.common import generate_token

from apps.devices.models import Device
from apps.users.models import User


async def create_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
) -> User:
    hashed_password = await sync_to_async(make_password)(password)
    return await User.objects.acreate(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=hashed_password,
    )


async def create_oauth_tokens(
    user: User,
    application: Application,
) -> tuple[AccessToken, RefreshToken]:
    expires_seconds = timezone.now() + timedelta(
        seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
    )
    access_token = await AccessToken.objects.acreate(
        user_id=user.id,
        token=generate_token(),
        application_id=application.id,
        expires=expires_seconds,
        scope=" ".join(oauth2_settings.DEFAULT_SCOPES),
    )
    refresh_token = await RefreshToken.objects.acreate(
        user_id=user.id,
        token=generate_token(),
        application_id=application.id,
        access_token_id=access_token.id,
    )
    return access_token, refresh_token


async def bind_access_token_to_device(
    access_token: AccessToken,
    device: Device,
) -> None:
    device.auth_token = access_token
    await device.asave(update_fields=["auth_token", "updated_timestamp"])


async def revoke_access_token(access_token: AccessToken) -> None:
    await RefreshToken.objects.filter(
        access_token_id=access_token.id,
    ).adelete()
    await access_token.adelete()


async def revoke_user_tokens(user: User) -> None:
    await RefreshToken.objects.filter(
        user_id=user.id,
    ).adelete()
    await AccessToken.objects.filter(user_id=user.id).adelete()


async def deactivate_user(user: User) -> User:
    user.is_active = False
    await user.asave(update_fields=["is_active"])
    return user
