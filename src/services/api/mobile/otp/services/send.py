from typing import final, override

from apps.otp.exceptions import OTPThrottledError
from apps.otp.services import (
    has_active_otp_code,
    send_code_task_delay,
    update_or_create_otp_code,
)
from services.api.mobile.common.service import BaseService
from services.api.mobile.otp.schemas import OTPSendRequest, OTPTokenResponse


@final
class OtpSendService(BaseService):
    @override
    async def execute(self, payload: OTPSendRequest) -> OTPTokenResponse:
        has_active_code, _existing_otp = await has_active_otp_code(
            payload.email,
        )
        if has_active_code:
            raise OTPThrottledError()

        otp_code = await update_or_create_otp_code(email=payload.email)
        await send_code_task_delay(
            code=otp_code.code,
            email=otp_code.email,
        )
        return OTPTokenResponse.model_validate(otp_code)
