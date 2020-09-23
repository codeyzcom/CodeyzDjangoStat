from redis import Redis

from cdzstat.settings import (
    CDZSTAT_REDIS_HOST,
    CDZSTAT_REDIS_PORT,
    CDZSTAT_REDIS_PASS,
)

default_app_config = 'cdzstat.apps.CdzstatConfig'

HTTP_STATUSES = (
    ('200', '200: OK'),
    ('301', '301: Moved Permanently'),
    ('403', '403: Forbidden'),
    ('404', '404: Not Found')
)

USER_AGENT_CACHE = []
EXCEPTION_CACHE_REGEX = {}
EXCEPTION_CACHE_DIRECT = {}

REDIS_CONN = Redis(
    host=CDZSTAT_REDIS_HOST,
    port=CDZSTAT_REDIS_PORT,
    password=CDZSTAT_REDIS_PASS,
    decode_responses=True
)


## Constants
ACTIVE_SESSIONS = 'cdzstat:registry:active_sessions'
SESSION_KEY = 'session_key'
REQUEST_COUNT = 'request_count'

