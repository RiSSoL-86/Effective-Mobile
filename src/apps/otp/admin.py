from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from apps.otp.models import OTPCode


class OTPCodeAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("id", "email", "status", "created_timestamp")
    search_fields = ("email",)
    list_filter = ("status",)
    readonly_fields = (
        "created_timestamp",
        "updated_timestamp",
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Any = None
    ) -> bool:
        return False


admin.site.register(OTPCode, OTPCodeAdmin)
