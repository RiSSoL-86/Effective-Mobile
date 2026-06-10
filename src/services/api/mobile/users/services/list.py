from typing import final, override

from apps.users.models import User
from services.api.mobile.common.service import BaseService
from services.api.mobile.users.exceptions import (
    UserAccessDeniedError,
    UserInactiveError,
)


@final
class UserListService(BaseService):
    """Return every application user. Restricted to staff members."""

    @override
    async def execute(self, requester: User) -> list[User]:
        if not requester.is_active:
            raise UserInactiveError()
        if not requester.is_staff:
            raise UserAccessDeniedError()
        return [user async for user in User.objects.order_by("id")]
