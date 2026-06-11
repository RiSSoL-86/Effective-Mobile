from typing import final, override

from apps.otp.choices import OTPCodeStatus
from apps.otp.exceptions import InvalidTokenError, OTPStatusError
from apps.otp.models import OTPCode
from apps.otp.services import send_code_task_delay, update_or_create_otp_code
from services.api.mobile.common.service import BaseService
from services.api.mobile.otp.schemas import OTPResendRequest, OTPTokenResponse


@final
class OtpResendService(BaseService):
    @override
    async def execute(self, payload: OTPResendRequest) -> OTPTokenResponse:
        otp_code = await OTPCode.objects.filter(
            otp_token=payload.otp_token,
        ).afirst()
        if otp_code is None:
            raise InvalidTokenError()

        if otp_code.status == OTPCodeStatus.USED:
            raise OTPStatusError()

        new_otp_code = await update_or_create_otp_code(email=otp_code.email)
        await send_code_task_delay(
            code=new_otp_code.code,
            email=new_otp_code.email,
        )
        return OTPTokenResponse.model_validate(new_otp_code)
