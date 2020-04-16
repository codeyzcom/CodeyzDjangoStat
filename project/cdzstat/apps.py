from django.apps import AppConfig


class CdzstatConfig(AppConfig):
    name = 'cdzstat'

    def ready(self):
        from . import signals
