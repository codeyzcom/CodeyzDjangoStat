import re
import time

from .settings import CDZSTAT_IGNORE_BOTS

from .models import (
    ExceptionPath,
    Request,
    UserAgent,
    IpAddress,
    Host,
    Path,
)

from .urls import get_ip

from . import (
    USER_AGENT_CACHE,
    EXCEPTION_CACHE_REGEX,
    EXCEPTION_CACHE_DIRECT,
)


class ExceptionService:

    def __init__(self, request):
        self._req = request

    def check(self):
        host = self._req.META.get('HTTP_HOST')
        path = self._req.path
        user_agent = self._req.META['HTTP_USER_AGENT']

        if CDZSTAT_IGNORE_BOTS and not USER_AGENT_CACHE:
            USER_AGENT_CACHE.extend(
                UserAgent.objects.filter(
                    is_bot=True
                ).order_by('data').values_list('data', flat=True)
            )

        if CDZSTAT_IGNORE_BOTS and user_agent in USER_AGENT_CACHE:
            return True

        if not EXCEPTION_CACHE_REGEX:
            EXCEPTION_CACHE_REGEX.extend(ExceptionPath.objects.filter(
                state=True,
                except_type='regex'
            ))

        for r in EXCEPTION_CACHE_REGEX:
            match = re.match(r.path, path, re.IGNORECASE)
            if match:
                return True

        if not EXCEPTION_CACHE_DIRECT:
            EXCEPTION_CACHE_DIRECT[host] = (
                ExceptionPath.objects.filter(state=True, host__host=host).all()
            )

        paths = EXCEPTION_CACHE_DIRECT.get(host)
        if paths and path in paths:
            return True


class LowLevelService:

    def __init__(self, request, response):
        self._req = request
        self._resp = response

    def process(self):
        elapsed = time.time() - self._req.start_time
        ip_address = get_ip(self._req)
        user_agent = self._req.META['HTTP_USER_AGENT']
        current_host = self._req.META.get('HTTP_HOST')
        current_path = self._req.path
        status_code = self._resp.status_code

        ip_addr_obj, created = IpAddress.objects.get_or_create(ip=ip_address)
        user_agent_obj, created = UserAgent.objects.get_or_create(
            data=user_agent
        )
        host_obj, created = Host.objects.get_or_create(host=current_host)

        path_obj, created = Path.objects.get_or_create(path=current_path)
        path_obj.host.add(host_obj.id)
        path_obj.save()

        Request.objects.create(
            ip=ip_addr_obj,
            ua=user_agent_obj,
            host=host_obj,
            path=path_obj,
            status_code=status_code,
            response_time=elapsed
        )
