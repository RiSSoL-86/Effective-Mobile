from typing import final, override

from apps.users.models import User
from services.api.mobile.common.service import BaseService
from services.api.mobile.users.exceptions import (
    UserAccessDeniedError,
    UserInactiveError,
    UserNotFoundError,
)


@final
class UserDetailService(BaseService):
    """Return a single user by id.

    A staff member may fetch anyone; a regular user may only fetch their
    own profile. Any other case is rejected before the lookup, so the
    existence of another user is never leaked.
    """

    @override
    async def execute(self, requester: User, user_id: int) -> User:
        if not requester.is_active:
            raise UserInactiveError()
        if not requester.is_staff and requester.id != user_id:
            raise UserAccessDeniedError()
        user = await User.objects.filter(id=user_id).afirst()
        if user is None:
            raise UserNotFoundError()
        return user
