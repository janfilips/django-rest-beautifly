from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = "ioi.profiles"
    verbose_name = "Profiles"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals
