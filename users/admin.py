from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "name", "surname", "is_staff", "is_active")
    search_fields = ("email", "name", "surname")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Профиль",
            {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")},
        ),
        ("Связи", {"fields": ("favorites", "skills")}),
        (
            "Права",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Даты", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions", "favorites", "skills")
