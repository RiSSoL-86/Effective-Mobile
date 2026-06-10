from http import HTTPStatus

from django.utils.functional import Promise


class CustomMessageException(Exception):
    """All subclasses of this class should follow the convention
    where the class name suffix is '...Error'.
    """

    custom_message: str | Promise | None = None
    field: str | None = None
    loc: list[str | int] | None = None
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

    def __init__(self, message: str | None = None):
        super().__init__(message or self.custom_message)
        if message is not None:
            self.custom_message = message
