from cdzstat import utils


class RequestResponseHandler:
    priority = 100
    ctx = {'new_session': True, 'session_key': None}

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
        raise NotImplementedError


class SessionHandler(RequestResponseHandler):
    priority = 10

    def process(self):
        print('Session handler')


class PermanentSessionHandler(RequestResponseHandler):
    priority = 15

    def process(self):
        print('PermanentSessionHandler')


class IpAddressHandler(RequestResponseHandler):
    priority = 20

    def process(self):
        print('IpAddressHandler')
        self.ctx['ip_address'] = utils.get_ip(self.ctx.get('request'))


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
