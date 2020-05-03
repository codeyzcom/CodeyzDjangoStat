import re
import time
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from . import (
    USER_AGENT_CACHE,
    EXCEPTION_CACHE_REGEX,
    EXCEPTION_CACHE_DIRECT,
)
from .settings import (
    CDZSTAT_IGNORE_BOTS,
    CDZSTAT_SESSION_COOKIE_NAME,
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


class SessionService:

    def __init__(self, request, response):
        self._req = request
        self._resp = response

    def process(self):
        session_key = self._req.COOKIES.get(CDZSTAT_SESSION_COOKIE_NAME)
        now = timezone.localtime()
        expire_date = now + timedelta(minutes=30)

        if session_key:
            exist = models.SessionData.objects.filter(
                key=session_key,
                expire_date__gt=now,
            ).first()
            if exist:
                models.SessionData.objects.filter(key=session_key).update(
                    expire_date=expire_date
                )
            else:
                session_key = None
        if not session_key:
            s_obj = models.SessionData.objects.create(
                expire_date=expire_date
            )
            session_key = s_obj.key

        self._resp.set_cookie(
            CDZSTAT_SESSION_COOKIE_NAME,
            session_key,
            expires=expire_date,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            httponly=settings.SESSION_COOKIE_HTTPONLY or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )


class LowLevelService:

    def __init__(self, request, response):
        self._req = request
        self._resp = response

    def process(self):
        elapsed = time.time() - self._req.start_time
        ip_address = utils.get_ip(self._req)
        user_agent = self._req.META['HTTP_USER_AGENT']
        current_host = self._req.META.get('HTTP_HOST')
        current_path = self._req.path
        status_code = self._resp.status_code

        ip_addr_obj, created = models.IpAddress.objects.get_or_create(
            ip=ip_address
        )
        user_agent_obj, created = models.UserAgent.objects.get_or_create(
            data=user_agent
        )
        host_obj, created = models.Host.objects.get_or_create(
            host=current_host
        )
        path_obj, created = models.Path.objects.get_or_create(
            path=current_path
        )
        path_obj.host.add(host_obj.id)
        path_obj.save()

        models.Request.objects.create(
            host=host_obj,
            path=path_obj,
            status_code=status_code,
            response_time=elapsed
        )


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
        pass
