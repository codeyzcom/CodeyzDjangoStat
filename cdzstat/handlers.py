from abc import ABC, abstractmethod


class Handler(ABC):

    @abstractmethod
    def process(self):
        pass


class RequestRequestAbstractHandler(Handler):
    priority = 100
    ctx = {}

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
        print(f'Session Handler: {self.priority} RO: {self.read_only}')


class UserPermanentAttributeHandler(RequestRequestAbstractHandler):
    priority = 15
    read_only = False

    def preprocessing(self):
        if not self.ctx.get('response'):
            self.read_only = True
        return True

    def process(self):
        print(f'Permanent attribute check: {self.priority} RO: {self.read_only}')


class IpAddressHandler(RequestRequestAbstractHandler):
    priority = 20

    def process(self):
        print(f'IpAddress Handler: {self.priority}')

