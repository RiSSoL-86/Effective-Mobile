from typing import Any, cast

from django.http import HttpResponse
from dmr.endpoint import Endpoint
from dmr.errors import ErrorType, global_error_handler
from pydantic.alias_generators import to_camel

from apps.common.exceptions import CustomMessageException


def api_error_handler(
    endpoint: Endpoint,
    controller: Any,
    exc: Exception,
) -> HttpResponse:
    if isinstance(exc, CustomMessageException):
        loc = exc.loc or [to_camel(str(exc.field))]
        return cast(
            HttpResponse,
            controller.to_error(
                controller.format_error(
                    str(exc.custom_message),
                    loc=loc,
                    error_type=ErrorType.user_msg,
                ),
                status_code=exc.status_code,
            ),
        )
    return global_error_handler(endpoint, controller, exc)
