import json
import re
import time
from urllib.parse import urlparse
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.utils import timezone

from . import (
    USER_AGENT_CACHE,
    EXCEPTION_CACHE_REGEX,
    EXCEPTION_CACHE_DIRECT,
    REDIS_CONN,
)
from .settings import (
    CDZSTAT_IGNORE_BOTS,
    CDZSTAT_SESSION_COOKIE_NAME,
    CDZSTAT_SESSION_COOKIE_AGE,
)
from cdzstat import (
    models,
    handlers,
    utils,
)


class ExceptionService:

    def __init__(self, request):
        self._req = request

    def check(self):
        host = self._req.META.get('HTTP_HOST')
        path = self._req.path
        user_agent = self._req.META['HTTP_USER_AGENT']

        if path == '/cdzstat/collect_statistic':
            return True

        if not CDZSTAT_IGNORE_BOTS and not USER_AGENT_CACHE:
            USER_AGENT_CACHE.extend(
                models.UserAgent.objects.filter(
                    is_bot=True
                ).order_by('data').values_list('data', flat=True)
            )

        if not CDZSTAT_IGNORE_BOTS and user_agent in USER_AGENT_CACHE:
            return True

        if not EXCEPTION_CACHE_REGEX:
            result = models.ExceptionPath.objects.filter(
                state=True,
                except_type='regex',
                host__host=host
            ).values_list('path', flat=True)
            EXCEPTION_CACHE_REGEX[host] = tuple(result)

        regex_path = EXCEPTION_CACHE_REGEX.get(host)
        if regex_path:
            for r in regex_path:
                match = re.match(r, path, re.IGNORECASE)
                if match:
                    return True

        if not EXCEPTION_CACHE_DIRECT:
            result = (
                models.ExceptionPath.objects.filter(
                    state=True,
                    except_type='match',
                    host__host=host
                ).values_list('path', flat=True)
            )
            EXCEPTION_CACHE_DIRECT[host] = tuple(result)

        direct_paths = EXCEPTION_CACHE_DIRECT.get(host)
        if direct_paths and path in direct_paths:
            return True


class LowLevelService:

    def __init__(self, request, response) -> None:
        self._req = request
        self._resp = response

    def process(self) -> None:
        session_key, data, navigate = self._collect_data()

        session_key = session_key[0]
        new_session = False

        if not session_key:
            new_session = True
        else:
            skey = REDIS_CONN.hgetall(utils.get_session(session_key))
            if not skey:
                new_session = True
            else:
                REDIS_CONN.expire(
                    utils.get_session(utils.get_session(session_key)),
                    CDZSTAT_SESSION_COOKIE_AGE
                )

        if new_session:
            session_key = str(uuid4())
            with REDIS_CONN.pipeline() as pipe:
                for k, v in data.items():
                    pipe.hset(utils.get_session(session_key), k, v)
                pipe.execute()
            REDIS_CONN.expire(utils.get_session(session_key), CDZSTAT_SESSION_COOKIE_AGE)

        REDIS_CONN.rpush(utils.get_navigation(session_key), json.dumps(navigate))

        self._resp.set_cookie(
            CDZSTAT_SESSION_COOKIE_NAME,
            session_key,
            expires=CDZSTAT_SESSION_COOKIE_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )

    def _collect_data(self) -> (str, dict, dict):
        session = self._req.COOKIES.get(CDZSTAT_SESSION_COOKIE_NAME),
        data = {
            'ip_address': utils.get_ip(self._req),
            'user_agent': self._req.META['HTTP_USER_AGENT'],
            'status_code': self._resp.status_code
        }
        navigate = {
            'host': self._req.META.get('HTTP_HOST'),
            'path': self._req.path,
            'referer': self._req.META.get('HTTP_REFERER') or '',
        }
        return session, data, navigate


class HeightLevelService:

    def __init__(self, request):
        self._req = request

    def process(self):
        full_data = json.loads(self._req.body.decode())

        hlist = list()
        hlist.append(handlers.DataHandler)
        hlist.append(handlers.ParamHandler)

        hlist.sort(key=lambda x: x.priority)

        for handler in hlist:
            if handler.state:
                handler(full_data).process()
