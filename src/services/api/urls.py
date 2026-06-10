from typing import TYPE_CHECKING

from django.urls import include, path
from dmr.openapi import build_schema
from dmr.openapi.views import SwaggerView
from dmr.plugins.pydantic import PydanticSerializer
from dmr.routing import Router, build_404_handler, build_500_handler

from services.api.common.services.openapi import OpenAPIJsonDownloadView
from services.api.mobile import urls as mobile_urls

if TYPE_CHECKING:
    from django.urls import URLPattern, URLResolver


router = Router(
    prefix="api/",
    urls=[
        path(
            mobile_urls.router.prefix,
            include((mobile_urls.router.urls, "mobile"), namespace="mobile"),
        ),
    ],
)

schema = build_schema(router)

urlpatterns: "list[URLPattern | URLResolver]" = [
    path(router.prefix, include((router.urls, "api"), namespace="api")),
    path(f"{router.prefix}docs/", SwaggerView.as_view(schema), name="docs"),
    path(
        f"{router.prefix}schema.json",
        OpenAPIJsonDownloadView.as_view(schema),
        name="schema-json",
    ),
]

handler404 = build_404_handler(
    router.prefix,
    serializer=PydanticSerializer,
)

handler500 = build_500_handler(
    router.prefix,
    serializer=PydanticSerializer,
)
