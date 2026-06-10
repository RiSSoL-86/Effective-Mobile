from dmr.routing import Router, path

from services.api.mobile.auth.controllers import (
    LogoutController,
    RefreshController,
    SigninController,
    SignupController,
)

router = Router(
    prefix="auth/",
    urls=[
        path("signup/", SignupController.as_view(), name="signup"),
        path("signin/", SigninController.as_view(), name="signin"),
        path("refresh/", RefreshController.as_view(), name="refresh"),
        path("logout/", LogoutController.as_view(), name="logout"),
    ],
)
