from django.conf import settings


def get(key, default):
    return getattr(settings, key, default)


CDZSTAT_IGNORE_BOTS = get('CDZSTAT_IGNORE_BOTS', True)

CDZSTAT_SESSION_COOKIE_NAME = get('CDZSTAT_SESSION_COOKIE_NAME', 'cdz_session')
CDZSTAT_SESSION_AGE = get('CDZSTAT_SESSION_AGE', 1800)
