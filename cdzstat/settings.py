from django.conf import settings


def get(key, default):
    return getattr(settings, key, default)


CDZSTAT_IGNORE_BOTS = get('CDZSTAT_IGNORE_BOTS', True)

CDZSTAT_SCRIPT_ID = '20200914879915'

CDZSTAT_SESSION_COOKIE_NAME = get('CDZSTAT_SESSION_COOKIE_NAME', 'cdz_session')
CDZSTAT_REQUEST_NUM_NAME = get('CDZSTAT_REQUEST_NUM_NAME', 'request_inc')
CDZSTAT_SESSION_AGE = get('CDZSTAT_SESSION_AGE', 1800)

CDZSTAT_PERMANENT_COOKIE_NAME = get(
	'CDZSTAT_PERMANENT_COOKIE_NAME', 'permanent_key'
	)
CDZSTAT_PERMANENT_COOKIE_AGE = get(
	'CDZSTAT_PERMANENT_COOKIE_AGE', 
	(5 * (365 * 24 * 60 * 60))
	)

CDZSTAT_REDIS_HOST = get('CDZSTAT_REDIS_HOST', 'localhost')
CDZSTAT_REDIS_PORT = get('CDZSTAT_REDIS_PORT', 6379)
CDZSTAT_REDIS_PASS = get('CDZSTAT_REDIS_PASS', '')

CDZSTAT_WORKERS_THREAD_NUMBER = get('CDZSTAT_WORKERS_THREAD_NUMBER', 2)

CDZSTAT_QUEUE_SESSION = get('CDZSTAT_QUEUE_SESSION', 'q_session')
