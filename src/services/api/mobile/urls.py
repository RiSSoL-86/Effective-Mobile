from django.urls import include
from dmr.routing import Router, path

from services.api.mobile.auth import urls as auth_urls
from services.api.mobile.devices import urls as devices_urls
from services.api.mobile.otp import urls as otp_urls
from services.api.mobile.users import urls as users_urls

router = Router(
    prefix="mobile/",
    urls=[
        path(
            devices_urls.router.prefix,
            include(
                (devices_urls.router.urls, "devices"),
                namespace="devices",
            ),
        ),
        path(
            auth_urls.router.prefix,
            include((auth_urls.router.urls, "auth"), namespace="auth"),
        ),
        path(
            users_urls.router.prefix,
            include((users_urls.router.urls, "users"), namespace="users"),
        ),
        path(
            otp_urls.router.prefix,
            include((otp_urls.router.urls, "otp"), namespace="otp"),
        ),
    ],
)
