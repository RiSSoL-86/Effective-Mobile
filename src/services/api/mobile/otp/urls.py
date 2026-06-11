from dmr.routing import Router, path

from services.api.mobile.otp.controllers import (
    OtpResendController,
    OtpSendController,
    OtpVerifyController,
)

router = Router(
    prefix="otp/",
    urls=[
        path("send/", OtpSendController.as_view(), name="send"),
        path("verify/", OtpVerifyController.as_view(), name="verify"),
        path("resend/", OtpResendController.as_view(), name="resend"),
    ],
)
