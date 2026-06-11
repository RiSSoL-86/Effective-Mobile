from dmr import Controller
from dmr.plugins.pydantic import PydanticSerializer
from oauth2_provider.models import AccessToken

from apps.users.models import User
from services.api.common.schemas import AuthData


class AuthenticatedController(Controller[PydanticSerializer]):
    @property
    def _auth_data(self) -> AuthData:
        """Helper property for retrieving authorization data."""
        auth = getattr(self.request, "auth", None)
        if not isinstance(auth, list | tuple):
            msg = (
                f"Controller '{self.__class__.__name__}' requires "
                "authentication. Make sure you have added "
                "'auth = [AuthBearer()]' to the controller."
            )
            raise AttributeError(msg)
        return AuthData(*auth)

    @property
    def user(self) -> User:
        return self._auth_data.user

    @property
    def token(self) -> AccessToken:
        return self._auth_data.token
