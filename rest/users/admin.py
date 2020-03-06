from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import forms, models


@admin.register(models.IoiUser)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = forms.UserChangeForm
    add_form = forms.UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["email", "is_admin", "is_investor", "is_active"]
    list_filter = ["is_active", "is_admin", "is_investor"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Extra", {"fields": ["nickname"]}),
        (
            "Permissions",
            {"fields": ["is_active", "is_admin", "is_investor", "jwt_secret"]},
        ),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {"classes": ["wide"], "fields": ["email", "password1", "password2"]}),
    )
    readonly_fields = ["jwt_secret"]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
