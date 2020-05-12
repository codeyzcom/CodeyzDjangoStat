from django.conf import settings


def get(key, default):
    return getattr(settings, key, default)


CDZSTAT_IGNORE_BOTS = get('CDZSTAT_IGNORE_BOTS', True)

CDZSTAT_SESSION_COOKIE_NAME = get('CDZSTAT_SESSION_COOKIE_NAME', 'cdz_session')
CDZSTAT_REQUEST_NUM_NAME = get('CDZSTAT_REQUEST_NUM_NAME', 'request_inc')
CDZSTAT_SESSION_AGE = get('CDZSTAT_SESSION_AGE', 1800)

CDZSTAT_REDIS_HOST = get('CDZSTAT_REDIS_HOST', 'localhost')
CDZSTAT_REDIS_PORT = get('CDZSTAT_REDIS_PORT', 6379)
CDZSTAT_REDIS_PASS = get('CDZSTAT_REDIS_PASS', '')
