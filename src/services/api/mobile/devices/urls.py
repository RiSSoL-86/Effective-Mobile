from dmr.routing import Router, path

from services.api.mobile.devices.controllers import DeviceInitController

router = Router(
    prefix="devices/",
    urls=[
        path("init/", DeviceInitController.as_view(), name="init"),
    ],
)
