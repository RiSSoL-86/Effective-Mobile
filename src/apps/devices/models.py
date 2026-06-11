from django.db import models
from django.utils.translation import gettext_lazy as _
from oauth2_provider.settings import oauth2_settings

from apps.common.choices import Language
from apps.common.models import TimeStampedAbstractModel, UUIAbstractModel
from apps.devices.choices import DeviceOSName


class Device(UUIAbstractModel, TimeStampedAbstractModel):
    """
    The model responsible for the devices (phone)
    firebase_token - for push notifications
    id - hashed to make it impossible to find the id of the devices during
        its initialization
    device_id - the device id is not in the database, but is given to the
        device when it is created
    """

    # Foreign keys
    auth_token = models.OneToOneField(
        oauth2_settings.ACCESS_TOKEN_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="device",
    )

    # Main fields
    device_id = models.CharField(
        verbose_name=_("device id"), max_length=200, unique=True
    )
    os_name = models.IntegerField(
        verbose_name=_("os name"), choices=DeviceOSName.choices
    )
    app_version = models.CharField(
        verbose_name=_("application version"), max_length=200
    )
    os_version = models.CharField(verbose_name=_("os version"), max_length=200)
    model = models.CharField(verbose_name=_("model"), max_length=200)
    language = models.IntegerField(
        _("language"), choices=Language.choices, default=Language.ENGLISH
    )
    firebase_token = models.CharField(
        verbose_name=_("firebase token"), max_length=255, null=True, blank=True
    )

    class Meta:
        verbose_name = _("device")
        verbose_name_plural = _("devices")

    def __str__(self) -> str:
        return self.device_id
