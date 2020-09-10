from cdzstat import utils


class RequestResponseHandler:
    priority = 100
    ctx = {'state': True, 'new_session': True, 'session_key': None}

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


class NodeHandler(RequestResponseHandler):
    priority = 35

    def process(self):
        pass


class TransitionHandler(RequestResponseHandler):
    priority = 40

    def process(self):
        pass


class AdjacencyHandler(RequestResponseHandler):
    priority = 40

    def process(self):
        pass
