from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "firstname",
        "lastname",
        'phonenumber',
        'address',
        'postal_code',
        'city',
        'info',
        
        "profile_picture_tag",
        "short_info",
        "join_date",
        "last_online",
        "member_id",
        "is_staff",
        "is_active",
    )

    readonly_fields = ["member_id", "last_online", "join_date"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "member_id",
                    "username",
                    "firstname",
                    "lastname",
                    "phonenumber",
                    "address",
                    "city",
                    "postal_code",
                    "info",
                    "profile_picture",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "join_date", "last_online")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    def short_info(self, obj):
        max_len = 30

        return obj.info[:max_len] + "..." if len(obj.info) > max_len else obj.info

    short_info.short_description = "Info"

    def profile_picture_tag(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.profile_picture.url,
            )
        return "-"

    profile_picture_tag.short_description = "Profile Picture"
    profile_picture_tag.allow_tags = True
