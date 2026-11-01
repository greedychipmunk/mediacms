from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm

from .models import PortalUserSettings, User


class AdminUserCreationForm(UserCreationForm):
    """Form used when adding a user through the Django admin.

    Adds working password fields (password1/password2) to the add form, so
    users created by admins get a usable password instead of an unusable one.
    """

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "name")


class UserAdmin(admin.ModelAdmin):
    search_fields = ["email", "username", "name"]
    exclude = ["user_permissions", "title", "password", "groups", "last_login", "is_featured", "location", "first_name", "last_name", "media_count", "date_joined", "is_active", "is_approved"]
    list_display = [
        "username",
        "name",
        "email",
        "logo",
        "date_added",
        "is_superuser",
        "is_editor",
        "is_manager",
        "media_count",
    ]
    list_filter = ["is_superuser", "is_editor", "is_manager"]
    ordering = ("-date_added",)

    add_form = AdminUserCreationForm
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("username", "email", "name", "password1", "password2")}),)

    def get_fieldsets(self, request, obj=None):
        """Show the creation form fields when adding a user."""
        if obj is None:
            return self.add_fieldsets
        # zero-argument super() binds the class at definition time, so this
        # keeps working if tests reload the users.admin module
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """Use the creation form (with password fields) when adding a user."""
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        # zero-argument super() binds the class at definition time, so this
        # keeps working if tests reload the users.admin module
        return super().get_form(request, obj, **defaults)

    if settings.USERS_NEEDS_TO_BE_APPROVED:
        list_display.append("is_approved")
        list_filter.append("is_approved")
        exclude.remove("is_approved")


class PortalUserSettingsAdmin(admin.ModelAdmin):
    """Admin for the singleton portal user settings."""

    def has_add_permission(self, request):
        # only a single settings row can exist
        return not PortalUserSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(User, UserAdmin)
admin.site.register(PortalUserSettings, PortalUserSettingsAdmin)
