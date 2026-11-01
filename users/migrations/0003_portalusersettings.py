import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_is_approved"),
    ]

    operations = [
        migrations.CreateModel(
            name="PortalUserSettings",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "user_registration_enabled",
                    models.BooleanField(
                        default=True,
                        help_text=("Whether users can register new accounts on their own. Managers and admins can" " always create users through the API or the Django admin."),
                        verbose_name="User registration enabled",
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="portal_settings_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Portal User Settings",
                "verbose_name_plural": "Portal User Settings",
            },
        ),
    ]
