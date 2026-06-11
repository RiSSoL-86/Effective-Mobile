import datetime

from services.api.common.schemas import CamelCaseModel


class TokenUser(CamelCaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    last_login: datetime.datetime | None = None
    date_joined: datetime.datetime | None = None


class TokenResponse(CamelCaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str | None = None
    user: TokenUser


class IntrospectTokenResponse(CamelCaseModel):
    active: bool
    scope: str | None = None
    exp: int | None = None
    client_id: str | None = None
    username: str | None = None
