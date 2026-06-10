from typing import final, override

from apps.otp.services import verify_otp
from services.api.mobile.common.service import BaseService
from services.api.mobile.otp.schemas import OTPVerifyRequest, OTPVerifyResponse


@final
class OtpVerifyService(BaseService):
    @override
    async def execute(self, payload: OTPVerifyRequest) -> OTPVerifyResponse:
        await verify_otp(
            otp_token=payload.otp_token,
            code=payload.code,
        )
        return OTPVerifyResponse()
