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
    RCONN,
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
        data = self._collect_data()

        new_session = False

        if not data.get('session_key', False):
            new_session = True
        else:
            skey = RCONN.get(data['session_key'])
            if not skey:
                new_session = True

        if new_session:
            skey = str(uuid4())
            data['session_key'] = skey
            RCONN.set(skey, json.dumps(data))
            RCONN.expire(skey, CDZSTAT_SESSION_COOKIE_AGE)

        self._resp.set_cookie(
            CDZSTAT_SESSION_COOKIE_NAME,
            data['session_key'],
            expires=CDZSTAT_SESSION_COOKIE_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )

    def _collect_data(self) -> dict:
        return {
            'session_key': self._req.COOKIES.get(CDZSTAT_SESSION_COOKIE_NAME),
            'ip_address': utils.get_ip(self._req),
            'user_agent': self._req.META['HTTP_USER_AGENT'],
            'host': self._req.META.get('HTTP_HOST'),
            'path': self._req.path,
            'referer': self._req.META.get('HTTP_REFERER'),
            'status_code': self._resp.status_code
        }


class HeightLevelService:

    def __init__(self, request):
        self._req = request

    def process(self):
        hlist = list()
        hlist.append(handlers.UserLanguageHandler)
        hlist.append(handlers.TimezoneHandler)
        hlist.append(handlers.ScreenSizeHandler)
        hlist.append(handlers.WindowSizeHandler)
        hlist.append(handlers.ColorParamHandler)
        hlist.append(handlers.BrowserHandler)
        hlist.append(handlers.SystemInfoHandler)

        hlist.sort(key=lambda x: x.priority)

        for handler in hlist:
            if handler.state:
                handler(self._req).exec()


class StatisticalService:

    def __init__(self, request):
        self._req = request

    def process(self):
        for k, v in json.loads(self._req.body).items():
            print(k, v)
