from cdzstat import utils


class RequestResponseHandler:
    priority = 100
    ctx = {
        'state': True, 'new_session': True, 'session_key': None,
    }

    def __init__(self, request, response):
        self.ctx['request'] = request
        self.ctx['response'] = response

    def check_state(self) -> bool:
        return self.ctx.get('state')

    def preprocessing(self):
        """
        if return False then process will be skip
        :return:
        """
        return True

    def process(self):
        raise NotImplementedError


class StoreHandler(RequestResponseHandler):
    priority = 99999

    def process(self):
        pass


class SessionHandler(RequestResponseHandler):
    priority = 10

    def process(self):
        pass


class PermanentSessionHandler(RequestResponseHandler):
    priority = 15

    def process(self):
        pass


class IpAddressHandler(RequestResponseHandler):
    priority = 20

    def process(self):
        request = self.ctx.get('request')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        self.ctx['ip_address'] = ip


class UserAgentHandler(RequestResponseHandler):
    priority = 25

    def process(self):
        self.ctx['user_agent'] = self.ctx.get(
            'request'
        ).META.get('HTTP_USER_AGENT')


class HttpHeadersHandler(RequestResponseHandler):
    priority = 30

    def process(self):
        request = self.ctx.get('request')
        self.ctx['content_type'] = request.content_type
        self.ctx['accepted_types'] = [
            (x.main_type, x.sub_type) for x in request.accepted_types
        ]


class NodeNativeHandler(RequestResponseHandler):
    priority = 40

    def process(self):
        request = self.ctx.get('request')
        self.ctx['node'] = request.path_info


class NodeScriptHandler(RequestResponseHandler):
    priority = 40

    def process(self):
        self.ctx['node'] = 'NODE cdz_scipt.js'


class TransitionNativeHandler(RequestResponseHandler):
    priority = 45

    def process(self):
        request = self.ctx.get('request')

        self.ctx['transition'] = {
            'to': self.ctx.get('node'),
            'from': request.META.get('HTTP_REFERER')
        }


class TransitionScriptHandler(RequestResponseHandler):
    priority = 45

    def process(self):
        request = self.ctx.get('request')

        self.ctx['transition'] = {
            'to': 'TO cdz_stat.js',
            'from': 'from cdz_stat.js'
        }


class AdjacencyHandler(RequestResponseHandler):
    priority = 50

    def process(self):
        pass
