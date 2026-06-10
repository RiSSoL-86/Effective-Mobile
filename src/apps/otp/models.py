from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedAbstractModel
from apps.otp.choices import OTPCodeStatus


class OTPCode(TimeStampedAbstractModel):
    email = models.EmailField(_("email"))
    code = models.IntegerField(_("code"))
    otp_token = models.CharField(_("token"), max_length=32)
    status = models.PositiveSmallIntegerField(
        _("status"), choices=OTPCodeStatus.choices
    )

    class Meta:
        verbose_name = _("one-time password")
        verbose_name_plural = _("one-time passwords")

    def __str__(self) -> str:
        return str(self.id)
