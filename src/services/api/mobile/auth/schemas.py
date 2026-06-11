from typing import Self

from pydantic import Field, model_validator

from services.api.common.schemas import CamelCaseModel
from services.api.mobile.auth.exceptions import (
    MismatchUserPasswordFieldsError,
)
from services.api.mobile.common.schemas import DeviceIdHeaders


class AuthHeaders(DeviceIdHeaders):
    client_id: str = Field(alias="CLIENT-ID", max_length=100)


class SignupRequest(CamelCaseModel):
    otp_token: str = Field(..., max_length=32)
    first_name: str = Field(..., max_length=80)
    last_name: str = Field(..., max_length=80)
    password: str = Field(..., max_length=128)
    password_repeat: str = Field(..., max_length=128)

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise MismatchUserPasswordFieldsError()
        return self


class SigninRequest(CamelCaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., max_length=128)


class AuthResponse(CamelCaseModel):
    email: str
    access_token: str
    refresh_token: str


class RefreshRequest(CamelCaseModel):
    refresh_token: str


class RefreshResponse(AuthResponse):
    pass
