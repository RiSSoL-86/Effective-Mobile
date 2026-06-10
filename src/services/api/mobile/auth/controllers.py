from http import HTTPStatus
from typing import final

from dmr import Body, Headers, ResponseSpec, modify

from services.api.common.auth import AuthBearer
from services.api.mobile.auth.schemas import (
    AuthHeaders,
    AuthResponse,
    RefreshRequest,
    RefreshResponse,
    SigninRequest,
    SignupRequest,
)
from services.api.mobile.auth.services.logout import LogoutService
from services.api.mobile.auth.services.refresh import RefreshService
from services.api.mobile.auth.services.signin import SigninService
from services.api.mobile.auth.services.signup import SignupService
from services.api.mobile.common.controllers import (
    MobileAuthenticatedController,
    MobileController,
)
from services.api.mobile.common.schemas import DeviceIdHeaders


@final
class SignupController(MobileController):
    @modify(
        status_code=HTTPStatus.CREATED,
        tags=["Auth"],
        extra_responses=[
            ResponseSpec(
                MobileController.error_model,
                status_code=HTTPStatus.CONFLICT,
            ),
        ],
    )
    async def post(
        self,
        parsed_body: Body[SignupRequest],
        parsed_headers: Headers[AuthHeaders],
    ) -> AuthResponse:
        device = await self.set_device(parsed_headers)
        service = SignupService()
        response = await service.execute(
            parsed_body,
            client_id=parsed_headers.client_id,
            device=device,
        )
        return AuthResponse.model_validate(response)


@final
class SigninController(MobileController):
    @modify(
        status_code=HTTPStatus.OK,
        tags=["Auth"],
        extra_responses=[
            ResponseSpec(
                MobileController.error_model,
                status_code=HTTPStatus.UNAUTHORIZED,
            ),
            ResponseSpec(
                MobileController.error_model,
                status_code=HTTPStatus.FORBIDDEN,
            ),
        ],
    )
    async def post(
        self,
        parsed_body: Body[SigninRequest],
        parsed_headers: Headers[AuthHeaders],
    ) -> AuthResponse:
        device = await self.set_device(parsed_headers)
        service = SigninService()
        response = await service.execute(
            parsed_body,
            client_id=parsed_headers.client_id,
            device=device,
        )
        return AuthResponse.model_validate(response)


@final
class RefreshController(MobileController):
    @modify(status_code=HTTPStatus.CREATED, tags=["Auth"])
    async def post(
        self,
        parsed_body: Body[RefreshRequest],
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> RefreshResponse:
        device = await self.set_device(parsed_headers)
        service = RefreshService()
        response = await service.execute(
            parsed_body,
            device=device,
        )
        return RefreshResponse.model_validate(response)


@final
class LogoutController(MobileAuthenticatedController):
    auth = [AuthBearer()]

    @modify(status_code=HTTPStatus.NO_CONTENT, tags=["Auth"])
    async def post(
        self,
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> None:
        await self.set_device(parsed_headers)
        service = LogoutService()
        await service.execute(self.token)
