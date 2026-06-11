from typing import final, override

from asgiref.sync import sync_to_async
from oauth2_provider.models import Application

from apps.devices.models import Device
from apps.users.models import User
from apps.users.services import (
    bind_access_token_to_device,
    create_oauth_tokens,
)
from services.api.mobile.auth.exceptions import (
    InvalidClientIDError,
    InvalidCredentialsError,
)
from services.api.mobile.auth.schemas import SigninRequest
from services.api.mobile.common.service import BaseService
from services.api.mobile.users.exceptions import UserInactiveError


@final
class SigninService(BaseService):
    @override
    async def execute(
        self,
        payload: SigninRequest,
        client_id: str,
        device: Device,
    ) -> dict[str, str]:
        user = await User.objects.filter(email__iexact=payload.email).afirst()
        if user is None or not await sync_to_async(user.check_password)(
            payload.password
        ):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise UserInactiveError()

        application = await Application.objects.filter(
            client_id=client_id
        ).afirst()
        if application is None:
            raise InvalidClientIDError()

        access_token, refresh_token = await create_oauth_tokens(
            user,
            application,
        )
        await bind_access_token_to_device(
            access_token=access_token,
            device=device,
        )
        return {
            "email": user.email,
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
        }
