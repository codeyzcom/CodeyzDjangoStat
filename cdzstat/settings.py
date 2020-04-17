from django.conf import settings


def get(key, default):
    return getattr(settings, key, default)


CDZSTAT_IGNORE_BOTS = get('CDZSTAT_IGNORE_BOTS', True)
