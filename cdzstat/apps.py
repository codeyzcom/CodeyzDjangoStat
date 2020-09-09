from django.apps import AppConfig


class CdzstatConfig(AppConfig):
    name = 'cdzstat'

    def ready(self):
        from . import signals  # noqa

        from cdzstat.services import ServiceUtils
        ServiceUtils.initialize_application()
        #ServiceUtils.initialize_data()
