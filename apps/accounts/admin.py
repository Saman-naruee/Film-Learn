from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "username", "first_name", "last_name", "role", "is_staff", "is_verified", "is_active")
    list_filter = ("role", "is_staff", "is_verified", "is_superuser", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    readonly_fields = ("date_joined", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username", "first_name", "last_name", "bio")}),
        (_("Permissions"), {"fields": ("role", "is_active", "is_staff", "is_superuser", "is_verified", "groups", "user_permissions")}),
        (_("Timestamps"), {"fields": ("date_joined", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_verified"),
        }),
    )
