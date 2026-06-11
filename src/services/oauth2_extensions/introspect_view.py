import json
from typing import final, override

from django.http import HttpResponse
from oauth2_provider.views.introspect import (
    IntrospectTokenView as BaseIntrospectTokenView,
)

from services.oauth2_extensions.schemas import IntrospectTokenResponse


@final
class IntrospectTokenView(BaseIntrospectTokenView):
    @override
    @staticmethod
    def get_token_response(token_value=None) -> HttpResponse:
        original_response = BaseIntrospectTokenView.get_token_response(
            token_value
        )
        data = json.loads(original_response.content)

        response_data = IntrospectTokenResponse(**data)

        return HttpResponse(
            content=response_data.model_dump_json(by_alias=True),
            status=original_response.status_code,
            headers=original_response.headers,
        )
