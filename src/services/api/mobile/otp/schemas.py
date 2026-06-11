from pydantic import Field

from services.api.common.schemas import CamelCaseModel


class OTPSendRequest(CamelCaseModel):
    email: str


class OTPResendRequest(CamelCaseModel):
    otp_token: str = Field(..., max_length=32)


class OTPVerifyRequest(CamelCaseModel):
    otp_token: str = Field(..., max_length=32)
    code: int


class OTPTokenResponse(CamelCaseModel):
    otp_token: str = Field(..., max_length=32)


class OTPVerifyResponse(CamelCaseModel):
    verified: bool = True
