from http import HTTPStatus
from typing import final

from dmr import Body, Headers, Path, modify

from services.api.common.auth import AuthBearer
from services.api.mobile.common.controllers import (
    MobileAuthenticatedController,
)
from services.api.mobile.common.schemas import DeviceIdHeaders
from services.api.mobile.users.path_params import UserPathParams
from services.api.mobile.users.schemas import (
    UserMeResponse,
    UserResponse,
    UserUpdateRequest,
)
from services.api.mobile.users.services.detail import UserDetailService
from services.api.mobile.users.services.list import UserListService
from services.api.mobile.users.services.me import (
    UserDeleteService,
    UserMeService,
    UserUpdateService,
)


@final
class UserMeController(MobileAuthenticatedController):
    auth = [AuthBearer()]

    @modify(status_code=HTTPStatus.OK, tags=["Users"])
    async def get(
        self,
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> UserMeResponse:
        await self.set_device(parsed_headers)
        service = UserMeService()
        response = await service.execute(self.user)
        return UserMeResponse.model_validate(response)

    @modify(status_code=HTTPStatus.OK, tags=["Users"])
    async def patch(
        self,
        parsed_body: Body[UserUpdateRequest],
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> UserMeResponse:
        await self.set_device(parsed_headers)
        service = UserUpdateService()
        response = await service.execute(self.user, parsed_body)
        return UserMeResponse.model_validate(response)

    @modify(status_code=HTTPStatus.NO_CONTENT, tags=["Users"])
    async def delete(
        self,
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> None:
        await self.set_device(parsed_headers)
        service = UserDeleteService()
        await service.execute(self.user)


@final
class UserDetailController(MobileAuthenticatedController):
    auth = [AuthBearer()]

    @modify(status_code=HTTPStatus.OK, tags=["Users"])
    async def get(
        self,
        parsed_path: Path[UserPathParams],
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> UserResponse:
        await self.set_device(parsed_headers)
        service = UserDetailService()
        user = await service.execute(self.user, parsed_path.user_id)
        return UserResponse.model_validate(user)


@final
class UserListController(MobileAuthenticatedController):
    auth = [AuthBearer()]

    @modify(status_code=HTTPStatus.OK, tags=["Users"])
    async def get(
        self,
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> list[UserResponse]:
        await self.set_device(parsed_headers)
        service = UserListService()
        users = await service.execute(self.user)
        return [UserResponse.model_validate(user) for user in users]
