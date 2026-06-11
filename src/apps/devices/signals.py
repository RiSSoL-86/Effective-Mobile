from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from oauth2_provider.models import AccessToken, RefreshToken

from apps.devices.models import Device


@receiver(post_save, sender=Device)
def delete_old_tokens(
    sender: type[Device], instance: Device, **kwargs: Any
) -> None:
    access_token = instance.auth_token
    if access_token:
        user_id = access_token.user_id
        application_id = access_token.application_id
        old_access_tokens = AccessToken.objects.filter(
            user_id=user_id,
            application_id=application_id,
            device__isnull=True,
        )
        old_access_tokens.delete()
        old_refresh_tokens = RefreshToken.objects.filter(
            user_id=user_id,
            application_id=application_id,
            access_token__isnull=True,
        )
        old_refresh_tokens.delete()
