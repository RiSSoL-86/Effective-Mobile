from pydantic import BaseModel


class UserPathParams(BaseModel):
    user_id: int
