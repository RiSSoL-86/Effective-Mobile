from django.contrib import admin

from apps.devices.models import Device


class DeviceAdmin(admin.ModelAdmin):  # type: ignore
    list_display = (
        "id",
        "auth_token",
        "device_id",
        "os_name",
        "app_version",
        "os_version",
        "model",
        "language",
    )
    search_fields = ("device_id",)
    list_filter = (
        "os_name",
        "language",
    )
    ordering = ("id",)


admin.site.register(Device, DeviceAdmin)
