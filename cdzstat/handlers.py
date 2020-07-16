from uuid import uuid4
from abc import ABC, abstractmethod

from django.conf import settings

from . import REDIS_CONN
from .settings import (
    CDZSTAT_SESSION_COOKIE_NAME,
    CDZSTAT_SESSION_AGE,
)
from . import utils


class Handler(ABC):

    @abstractmethod
    def process(self):
        pass


class RequestRequestAbstractHandler(Handler):
    priority = 100
    ctx = {'new_session': True}

    def __init__(self, request, response):
        self.ctx['request'] = request
        self.ctx['response'] = response

    def preprocessing(self):
        """
        if return False then process will be skip
        :return:
        """
        return True

    def process(self):
        print('Default behaviour')


class SessionHandler(RequestRequestAbstractHandler):
    priority = 10
    read_only = False

    def preprocessing(self):
        if not self.ctx.get('response'):
            self.read_only = True
        return True

    def process(self):
        session_key = self.ctx.get('request').COOKIES.get(
            CDZSTAT_SESSION_COOKIE_NAME
        )

        if session_key:
            if REDIS_CONN.exists(utils.get_session(session_key)):
                self.ctx['expired_session'] = False
                self.ctx['new_session'] = False
            else:
                self.ctx['expired_session'] = True
                REDIS_CONN.lpush(utils.get_gc(), session_key)

        if self.ctx['new_session']:
            session_key = str(uuid4())
            with REDIS_CONN.pipeline() as pipe:
                pipe.hset(
                    utils.get_session(session_key),
                    'created_at',
                    str(utils.get_dt())
                )
                pipe.expire(
                    utils.get_session(session_key), CDZSTAT_SESSION_AGE
                )
                pipe.execute()
        else:
            REDIS_CONN.expire(
                utils.get_session(session_key), CDZSTAT_SESSION_AGE
            )

        if not self.read_only:
            self.ctx.get('response').set_cookie(
                CDZSTAT_SESSION_COOKIE_NAME,
                session_key,
                expires=CDZSTAT_SESSION_AGE,
                path=settings.SESSION_COOKIE_PATH,
                secure=settings.SESSION_COOKIE_SECURE or None,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )

        self.ctx['session_key'] = session_key


class UserPermanentAttributeHandler(RequestRequestAbstractHandler):
    priority = 15
    read_only = False

    def preprocessing(self):
        if not self.ctx.get('response'):
            self.read_only = True
        return True

    def process(self):
        print(
            f'Permanent attribute check: {self.priority} RO: {self.read_only}'
            f'\nPermanent: {self.ctx}'
        )



class IpAddressHandler(RequestRequestAbstractHandler):
    priority = 20

    def process(self):
        print(f'IpAddress Handler: {self.priority}')
