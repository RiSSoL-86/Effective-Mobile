from pydantic import Field

from services.api.common.schemas import CamelCaseModel


class UserMeResponse(CamelCaseModel):
    id: int
    email: str
    first_name: str = Field(..., max_length=80)
    last_name: str = Field(..., max_length=80)
    is_active: bool


class UserUpdateRequest(CamelCaseModel):
    first_name: str | None = Field(default=None, max_length=80)
    last_name: str | None = Field(default=None, max_length=80)


class UserResponse(CamelCaseModel):
    id: int
    email: str
    first_name: str = Field(..., max_length=80)
    last_name: str = Field(..., max_length=80)
    is_active: bool
