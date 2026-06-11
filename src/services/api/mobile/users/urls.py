from dmr.routing import Router, path

from services.api.mobile.users.controllers import (
    UserDetailController,
    UserListController,
    UserMeController,
)

router = Router(
    prefix="users/",
    urls=[
        path("me/", UserMeController.as_view(), name="me"),
        path(
            "<int:user_id>/",
            UserDetailController.as_view(),
            name="detail",
        ),
        path("", UserListController.as_view(), name="list"),
    ],
)
