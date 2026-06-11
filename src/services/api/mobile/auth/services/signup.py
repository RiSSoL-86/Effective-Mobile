from typing import final, override

from oauth2_provider.models import Application

from apps.devices.models import Device
from apps.otp.services import get_verified_otp, mark_as_used
from apps.users.models import User
from apps.users.services import (
    bind_access_token_to_device,
    create_oauth_tokens,
    create_user,
)
from services.api.mobile.auth.exceptions import (
    InvalidClientIDError,
    UserAlreadyExistsError,
)
from services.api.mobile.auth.schemas import SignupRequest
from services.api.mobile.common.service import BaseService


@final
class SignupService(BaseService):
    @override
    async def execute(
        self,
        payload: SignupRequest,
        client_id: str,
        device: Device,
    ) -> dict[str, str]:
        otp = await get_verified_otp(payload.otp_token)

        if (
            await User.objects.filter(email__iexact=otp.email).afirst()
            is not None
        ):
            raise UserAlreadyExistsError()

        application = await Application.objects.filter(
            client_id=client_id
        ).afirst()
        if application is None:
            raise InvalidClientIDError()

        user = await create_user(
            email=otp.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=payload.password,
        )
        access_token, refresh_token = await create_oauth_tokens(
            user,
            application,
        )
        await bind_access_token_to_device(
            access_token=access_token,
            device=device,
        )
        await mark_as_used(otp)
        return {
            "email": user.email,
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
        }
