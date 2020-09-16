import json
from uuid import uuid4

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from cdzstat import (
    REDIS_CONN,
    ACTIVE_SESSIONS,
    utils,
)
from cdzstat.settings import (
    CDZSTAT_SCRIPT_ID,
    CDZSTAT_SESSION_COOKIE_NAME,
    CDZSTAT_REQUEST_NUM_NAME,
    CDZSTAT_SESSION_AGE,
)


class RequestResponseHandler:

    # session_data = {}
    # requeset_data = {}

    def __init__(self, context: dict) -> None:
        self.ctx = context

    def preprocessing(self):
        """
        if return False then process will be skip
        :return:
        """
        return True

    def process(self):
        raise NotImplementedError


class StoreHandler(RequestResponseHandler):
    priority = 9999

    def process(self):
        name = f'session:{self.ctx.get("session_key")}'
        request_data = json.dumps(self.ctx.get('requeset_data'))

        if self.ctx.get("session_key"):
            request_inc = self.ctx.get('request_inc')

            if self.ctx.get('kind') == 'native':
                REDIS_CONN.hset(name, f'{request_inc}_native', request_data)
            elif self.ctx.get('kind') == 'script':
                REDIS_CONN.hset(name, f'{request_inc}_script', request_data)
        else:
            REDIS_CONN.lpush(
                'anonymous_requests', json.dumps(self.ctx.get('requeset_data')
                                                 ))


class SessionGetterHandler(RequestResponseHandler):
    priority = 10

    def process(self):
        request = self.ctx.get('request')

        cookies = request.COOKIES

        if cookies:
            session_key = cookies.get(CDZSTAT_SESSION_COOKIE_NAME)
            request_inc = cookies.get(CDZSTAT_REQUEST_NUM_NAME)
            if session_key and bool(REDIS_CONN.hexists(ACTIVE_SESSIONS, session_key)):
                self.ctx['new_session'] = False
                self.ctx['session_key'] = session_key
                self.ctx['request_inc'] = request_inc
                return
        self.ctx['new_session'] = True
        self.ctx['session_key'] = None


class SessionSetterHandler(RequestResponseHandler):
    priority = 15

    def preprocessing(self):
        return self.ctx.get('new_session')

    def process(self):
        response = self.ctx.get('response')

        session_key = str(uuid4())
        now = utils.get_dt()
        request_inc = 1
        value = json.dumps({
            'request_inc': request_inc,
            'created_at': now,
            'updated_at': now,
        },
            cls=DjangoJSONEncoder
        )

        REDIS_CONN.hset(ACTIVE_SESSIONS, key=session_key, value=value)

        self.ctx['request_inc'] = request_inc
        self.ctx['session_key'] = session_key

        response.set_cookie(
            CDZSTAT_SESSION_COOKIE_NAME,
            session_key,
            expires=CDZSTAT_SESSION_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )

        response.set_cookie(
            CDZSTAT_REQUEST_NUM_NAME,
            request_inc,
            expires=CDZSTAT_SESSION_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )


class SessionUpdateHandler(RequestResponseHandler):
    priority = 15

    def preprocessing(self):
        if not self.ctx.get('new_session') and self.ctx.get('session_key'):
            return True

    def process(self):
        response = self.ctx.get('response')
        session_key = self.ctx.get('session_key')

        raw_data = REDIS_CONN.hget(ACTIVE_SESSIONS, session_key)
        data = json.loads(raw_data)
        request_inc = data.get('request_inc', 1) + 1
        data['request_inc'] = request_inc
        data['updated_at'] = utils.get_dt()
        value = json.dumps(data, cls=DjangoJSONEncoder)
        REDIS_CONN.hset(ACTIVE_SESSIONS, session_key, value=value)

        self.ctx['request_inc'] = request_inc

        response.set_cookie(
            CDZSTAT_SESSION_COOKIE_NAME,
            session_key,
            expires=CDZSTAT_SESSION_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )

        response.set_cookie(
            CDZSTAT_REQUEST_NUM_NAME,
            request_inc,
            expires=CDZSTAT_SESSION_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )


class PermanentSessionHandler(RequestResponseHandler):
    priority = 20

    def process(self):
        pass


class ScriptInitHandler(RequestResponseHandler):
    priority = 5

    def process(self):
        request = self.ctx.get('request')

        if not request.body:
            self.ctx['state'] = False
            return

        payload = json.loads(request.body)

        if str(payload.get('cdzscript')) != CDZSTAT_SCRIPT_ID:
            self.ctx['state'] = False
            return

        self.ctx['payload'] = payload


class IpAddressHandler(RequestResponseHandler):
    priority = 25

    def process(self):
        request = self.ctx.get('request')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        self.ctx['requeset_data']['ip_address'] = ip


class UserAgentHandler(RequestResponseHandler):
    priority = 30

    def process(self):
        self.ctx['session_data']['user_agent'] = self.ctx.get(
            'request'
        ).META.get('HTTP_USER_AGENT')


class HttpHeadersHandler(RequestResponseHandler):
    priority = 35

    def process(self):
        request = self.ctx.get('request')
        self.ctx['requeset_data']['content_type'] = request.content_type
        self.ctx['requeset_data']['accepted_types'] = [
            (x.main_type, x.sub_type) for x in request.accepted_types
        ]


class NodeNativeHandler(RequestResponseHandler):
    priority = 40

    def process(self):
        request = self.ctx.get('request')
        self.ctx['requeset_data']['node'] = request.path_info


class NodeScriptHandler(RequestResponseHandler):
    priority = 40

    def process(self):
        self.ctx['requeset_data']['node'] = 'NODE cdz_scipt.js'


class TransitionNativeHandler(RequestResponseHandler):
    priority = 45

    def process(self):
        request = self.ctx.get('request')

        self.ctx['requeset_data']['transition'] = {
            'to': self.ctx.get('node_native'),
            'from': request.META.get('HTTP_REFERER')
        }


class TransitionScriptHandler(RequestResponseHandler):
    priority = 45

    def process(self):
        request = self.ctx.get('request')

        self.ctx['requeset_data']['transition'] = {
            'to': self.ctx.get('node_script'),
            'from': 'from cdz_stat.js'
        }


class AdjacencyHandler(RequestResponseHandler):
    priority = 50

    def process(self):
        pass


class AdvancedParamScriptHandler(RequestResponseHandler):
    priority = 55

    def process(self):
        params = self.ctx.get('payload').get('params')
        view_params = {
            'screen_width': params.get('screen_width'),
            'screen_height': params.get('screen_height'),
            'window_width': params.get('window_width'),
            'window_height': params.get('window_height'),
            'screen_color_depth': params.get('screen_color_depth'),
            'screen_pixel_depth': params.get('screen_pixel_depth'),
        }
        self.ctx['requeset_data']['view_params'] = view_params


class SpeedScriptHandler(RequestResponseHandler):
    priority = 60

    def process(self):
        params = self.ctx.get('payload').get('speed')
        speed_params = {
            'processing': params.get('processing'),
            'loadingTime': params.get('loadingTime'),
        }
        self.ctx['requeset_data']['speed_params'] = speed_params
