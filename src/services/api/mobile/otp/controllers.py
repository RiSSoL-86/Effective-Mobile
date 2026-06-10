from http import HTTPStatus
from typing import final

from dmr import Body, Headers, ResponseSpec, modify

from services.api.mobile.common.controllers import MobileController
from services.api.mobile.common.schemas import DeviceIdHeaders
from services.api.mobile.otp.schemas import (
    OTPResendRequest,
    OTPSendRequest,
    OTPTokenResponse,
    OTPVerifyRequest,
    OTPVerifyResponse,
)
from services.api.mobile.otp.services.resend import OtpResendService
from services.api.mobile.otp.services.send import OtpSendService
from services.api.mobile.otp.services.verify import OtpVerifyService


@final
class OtpSendController(MobileController):
    @modify(
        status_code=HTTPStatus.CREATED,
        tags=["OTP"],
        extra_responses=[
            ResponseSpec(
                MobileController.error_model,
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
            ),
        ],
    )
    async def post(
        self,
        parsed_body: Body[OTPSendRequest],
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> OTPTokenResponse:
        await self.set_device(parsed_headers)
        service = OtpSendService()
        return await service.execute(parsed_body)


@final
class OtpVerifyController(MobileController):
    @modify(status_code=HTTPStatus.OK, tags=["OTP"])
    async def post(
        self,
        parsed_body: Body[OTPVerifyRequest],
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> OTPVerifyResponse:
        await self.set_device(parsed_headers)
        service = OtpVerifyService()
        return await service.execute(parsed_body)


@final
class OtpResendController(MobileController):
    @modify(status_code=HTTPStatus.CREATED, tags=["OTP"])
    async def post(
        self,
        parsed_body: Body[OTPResendRequest],
        parsed_headers: Headers[DeviceIdHeaders],
    ) -> OTPTokenResponse:
        await self.set_device(parsed_headers)
        service = OtpResendService()
        return await service.execute(parsed_body)
