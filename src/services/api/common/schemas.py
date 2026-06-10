from typing import NamedTuple

from oauth2_provider.models import AccessToken
from pydantic import AliasGenerator, BaseModel, ConfigDict, alias_generators

from apps.users.models import User


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=alias_generators.to_camel,
            serialization_alias=alias_generators.to_camel,
        ),
        validate_by_name=True,
        validate_by_alias=True,
        from_attributes=True,
    )


class AuthData(NamedTuple):
    user: User
    token: AccessToken
