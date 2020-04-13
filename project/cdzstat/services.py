import re

from .models import ExceptionPath


class ExceptionService:

    def __init__(self, request):
        self._req = request

    def check(self):
        host = self._req.META.get('HTTP_HOST')
        path = self._req.path

        regex_exc = ExceptionPath.objects.filter(
            state=True,
            except_type='regex'
        ).all()

        for r in regex_exc:
            match = re.match(r.path, path, re.IGNORECASE)
            if match:
                return True

        exc = ExceptionPath.objects.filter(
            state=True,
            host__host=host,
            path__exact=path
        )
        return True if exc else False
