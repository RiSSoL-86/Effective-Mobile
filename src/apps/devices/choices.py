from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceOSName(models.IntegerChoices):
    IOS = 0, _("ios")
    ANDROID = 1, _("android")
