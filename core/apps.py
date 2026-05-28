from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from django.utils import timezone

        from core.datetime_br import TZ_BR

        timezone.activate(TZ_BR)
