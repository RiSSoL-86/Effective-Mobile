from django.db import models
from django.utils.translation import gettext_lazy as _


class OTPCodeStatus(models.IntegerChoices):
    SENT = 0, _("sent")
    VERIFIED = 1, _("verified")
    USED = 2, _("used")
