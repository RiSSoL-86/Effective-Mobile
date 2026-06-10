from typing import TYPE_CHECKING, final, override

from dmr.openapi.views import OpenAPIJsonView

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@final
class OpenAPIJsonDownloadView(OpenAPIJsonView):
    @override
    def get(self, request: "HttpRequest") -> "HttpResponse":
        response = super().get(request)
        response["Content-Disposition"] = 'attachment; filename="schema.json"'
        return response
