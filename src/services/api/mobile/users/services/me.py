from typing import TYPE_CHECKING, final, override

from apps.users.services import deactivate_user, revoke_user_tokens
from services.api.mobile.common.service import BaseService
from services.api.mobile.users.exceptions import UserInactiveError
from services.api.mobile.users.schemas import UserUpdateRequest

if TYPE_CHECKING:
    from apps.users.models import User


@final
class UserMeService(BaseService):
    @override
    async def execute(self, user: "User") -> "User":
        if not user.is_active:
            raise UserInactiveError()
        return user


@final
class UserUpdateService(BaseService):
    @override
    async def execute(
        self,
        user: "User",
        payload: UserUpdateRequest,
    ) -> "User":
        if not user.is_active:
            raise UserInactiveError()
        update_fields = payload.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        for field, value in update_fields.items():
            setattr(user, field, value)
        if update_fields:
            await user.asave(update_fields=list(update_fields))
        return user


@final
class UserDeleteService(BaseService):
    @override
    async def execute(self, user: "User") -> None:
        if not user.is_active:
            raise UserInactiveError()
        await deactivate_user(user)
        await revoke_user_tokens(user)
