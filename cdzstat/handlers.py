from abc import abstractmethod

from . import REDIS_CONN
from cdzstat import utils


class AbstractHandler:
    priority = 100
    state = True
    ctx = dict()

    def __init__(self, full_data):
        self._full_data = full_data

    @abstractmethod
    def process(self) -> None:
        pass

    def get_ctx(self):
        return self.ctx


class DataHandler(AbstractHandler):

    priority = 10

    def process(self) -> None:
        data = self._full_data['data']
        session_key = data['session_key']

        is_anonymous = False

        if session_key:
            skey_obj = REDIS_CONN.hgetall(utils.get_session(session_key))
            if not skey_obj:
                is_anonymous = True
        else:
            is_anonymous = True

        if not is_anonymous:
            self.ctx['session_key'] = session_key
        # ToDo anonymous session 


class ParamHandler(AbstractHandler):

    def process(self) -> None:
        param = self._full_data['param']
        session_key = self.ctx['session_key']

        with REDIS_CONN.pipeline() as pipe:
            for k, v in param.items():
                pipe.hset(utils.get_session(session_key), k, v)
            pipe.execute()
