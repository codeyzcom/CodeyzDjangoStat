import re
import time
from urllib.parse import urlparse
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
    data = dict()

    def __init__(self, request, response):
        self._req = request
        self._resp = response

    def process(self):
        session_key = self._req.COOKIES.get(CDZSTAT_SESSION_COOKIE_NAME)
        now = timezone.localtime()
        expire_date = now + timedelta(minutes=30)
        self.data['created'] = False

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
            self.data['created'] = True

        self.data['session_key'] = session_key
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

    def __init__(
            self, request, response, session_data: dict) -> None:
        self._req = request
        self._resp = response
        self.s_data = session_data

    def process(self) -> None:
        elapsed = time.time() - self._req.start_time
        ip_address = utils.get_ip(self._req)
        user_agent = self._req.META['HTTP_USER_AGENT']
        current_host = self._req.META.get('HTTP_HOST')
        current_path = self._req.path
        referer_full_path = self._req.META.get('HTTP_REFERER')
        status_code = self._resp.status_code
        is_external_referer = False
        ext_ref_obj = None
        int_ref_obj = None

        ip_addr_obj, created = models.IpAddress.objects.get_or_create(
            ip=ip_address
        )
        user_agent_obj, created = models.UserAgent.objects.get_or_create(
            data=user_agent
        )
        path_obj, created = models.Path.objects.get_or_create(
            path=current_path
        )
        host_obj, created = models.Host.objects.get_or_create(
            host=current_host
        )

        path_obj.host.add(host_obj.id)
        path_obj.save()

        if referer_full_path:
            clear_ref = urlparse(referer_full_path)
            ref_host = clear_ref.netloc
            ref_path = clear_ref.path

            if models.Host.objects.filter(host=ref_host).first():
                int_ref_obj = models.Path.objects.filter(path=ref_path).first()
            else:
                is_external_referer = True
                ext_ref_obj, c = models.ExternalReferer.objects.get_or_create(
                    data=referer_full_path
                )

        session = models.SessionData.objects.filter(
            key=self.s_data.get('session_key')
        ).first()

        session.ip = ip_addr_obj
        session.ua = user_agent_obj
        session.save()

        if self.s_data.get('created', False) or is_external_referer:
            entry_point = True
        else:
            entry_point = False

        models.Request.objects.create(
            host=host_obj,
            path=path_obj,
            session=session,
            referer=int_ref_obj,
            external_referer=ext_ref_obj,
            entry_point=entry_point,
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
