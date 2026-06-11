from typing import Any

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from apps.devices.models import Device
from apps.users.models import User


@receiver(pre_delete, sender=User)
def delete_user_devices(
    sender: type[User],
    instance: User,
    **kwargs: Any,
) -> None:
    Device.objects.filter(auth_token__user_id=instance.id).delete()
