from typing import final, override

from oauth2_provider.models import AccessToken

from apps.users.services import revoke_access_token
from services.api.mobile.common.service import BaseService


@final
class LogoutService(BaseService):
    @override
    async def execute(self, access_token: AccessToken) -> None:
        await revoke_access_token(access_token)
