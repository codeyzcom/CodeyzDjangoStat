import json
import re
import time
from uuid import uuid4

from django.conf import settings

from . import (
    USER_AGENT_CACHE,
    EXCEPTION_CACHE_REGEX,
    EXCEPTION_CACHE_DIRECT,
    REDIS_CONN,
)
from .settings import (
    CDZSTAT_IGNORE_BOTS,
    CDZSTAT_SESSION_COOKIE_NAME,
    CDZSTAT_SESSION_AGE,
    CDZSTAT_REQUEST_NUM_NAME,
    CDZSTAT_QUEUE_SESSION,
)
from cdzstat import (
    models,
    utils,
)


class ServiceUtils:

    def __init__(self):
        pass

    @staticmethod
    def initialize_data():
        hosts = models.Host.objects.values_list('host', flat=True)

        REDIS_CONN.delete(utils.get_static('hosts'))
        for host in hosts:
            REDIS_CONN.sadd(utils.get_static('hosts'), host)

    @staticmethod
    def check_entry_point(referer, path):
        result = True
        if path:
            result = not REDIS_CONN.sismember(
                utils.get_static('hosts'), referer
            )
        return result


class NotifyService:

    def __init__(self):
        pass

    @staticmethod
    def send_notify(channel: str, data: str) -> None:
        REDIS_CONN.publish(channel, data)


class StoreService:

    def __init__(self):
        pass

    @staticmethod
    def add_session_data(data: dict, session: str = None) -> str:
        if session is None:
            session = str(uuid4())
        with REDIS_CONN.pipeline() as pipe:
            for k, v in data.items():
                pipe.hset(utils.get_session(session), k, v)
            pipe.execute()
        return session

    @staticmethod
    def session_exists(session: str) -> bool:
        if session is None:
            return False
        return bool(REDIS_CONN.exists(utils.get_session(session)))

    @staticmethod
    def add_node(session: str, path: str):
        REDIS_CONN.hset(
            utils.get_node(session),
            path,
            json.dumps({'dt_create': str(utils.get_dt()), 'counter': 1})
        )

    @staticmethod
    def inc_node(session: str, path: str):
        data = REDIS_CONN.hget(utils.get_node(session), path)
        data = json.loads(data)
        data['counter'] += 1
        REDIS_CONN.hset(utils.get_node(session), path, json.dumps(data))

    @staticmethod
    def check_node(session: str, path):
        return REDIS_CONN.hexists(utils.get_node(session), path)

    @staticmethod
    def add_transition(session: str, from_node: str, to_node: str) -> int:
        return REDIS_CONN.rpush(
            utils.get_transition(session),
            json.dumps({
                'from': from_node,
                'to': to_node,
                'dt_create': str(utils.get_dt())
            })
        )

    @staticmethod
    def update_transition(session: str, index: int, data: dict,
                          safe: bool = False) -> None:
        index = int(index) - 1
        if safe:
            exist_data = REDIS_CONN.lindex(
                utils.get_transition(session), index
            )
            exist_data = json.loads(exist_data)
            exist_data.update(data)
            data = exist_data
        data['last_change'] = str(utils.get_dt())
        REDIS_CONN.lset(utils.get_transition(session), index, json.dumps(data))

    @staticmethod
    def get_transition(session: str, index: int) -> dict:
        index = int(index) - 1
        result = REDIS_CONN.lindex(utils.get_transition(session), index)
        return json.loads(result)

    @staticmethod
    def get_transition_all(session: str) -> dict:
        result = REDIS_CONN.lrange(utils.get_transition(session), 0, -1)
        return json.loads(result)

    @staticmethod
    def add_adjacency(session: str, node: str, transition: int):
        transitions = [transition]
        adjacency = REDIS_CONN.hget(utils.get_adjacency(session), node)
        if adjacency:
            adjacency = json.loads(adjacency)
            transitions.extend(adjacency)
        return REDIS_CONN.hset(
            utils.get_adjacency(session),
            node,
            json.dumps(transitions)
        )

    @staticmethod
    def get_adjacency(session: str, key: str) -> list:
        result = REDIS_CONN.hget(utils.get_adjacency(session), key)
        return json.loads(result)

    @staticmethod
    def get_adjacency_all(session: str) -> dict:
        return REDIS_CONN.hgetall(utils.get_adjacency(session))

    @staticmethod
    def set_expire_all(session: str) -> None:
        with REDIS_CONN.pipeline() as pipe:
            pipe.expire(utils.get_session(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_node(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_transition(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_adjacency(session), CDZSTAT_SESSION_AGE)
            pipe.execute()

    @staticmethod
    def to_json(session):
        session_data = REDIS_CONN.hgetall(utils.get_session(session))
        node_data = REDIS_CONN.hgetall(utils.get_node(session))
        adjacency_data = REDIS_CONN.hgetall(utils.get_adjacency(session))
        transition_data = REDIS_CONN.lrange(
            utils.get_transition(session), 0, -1)

        return json.dumps({
            'session': session_data,
            'node': node_data,
            'transition': transition_data,
            'adjacency': adjacency_data
        })


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


class LowLevelService:

    def __init__(self, request, response) -> None:
        self._req = request
        self._resp = response

    def process(self) -> None:
        collected_data = self._collect_data()

        navigate = collected_data.get('navigate')
        d_data = collected_data.get('data_dynamic')

        session_key = collected_data.get('session')
        new_session = False

        current_path = navigate.get('path')
        current_referer = navigate.get('referer')
        referer = utils.split_url(current_referer)

        response_data = {
            'status_code': d_data.get('status_code'),
            'response_time': d_data.get('response_time'),
            'entry_point': ServiceUtils.check_entry_point(
                referer['host'],
                referer['path']
            )
        }

        """
        Checking - if the session exists in cookies and in the data store, 
        if not, set flag 'new_session' True.
        """
        if not session_key:
            new_session = True
        else:
            if not StoreService.session_exists(session_key):
                new_session = True

        if new_session:
            session_key = StoreService.add_session_data(
                {'user_agent': collected_data.get('user_agent')}, session_key
            )

        """
        Checking - if the node exists in data store, if exist - update data
        else add new node.
        """
        if StoreService.check_node(session_key, current_path):
            StoreService.inc_node(session_key, current_path)
        else:
            StoreService.add_node(session_key, current_path)

        """
        Each time add a new transition to the data store. After add 
        additional information. 
        """
        transition = StoreService.add_transition(
            session_key, referer['path'], current_path
        )
        StoreService.update_transition(
            session_key, transition, response_data, True
        )

        """
        Each time add adjacency
        """
        StoreService.add_adjacency(session_key, current_path, transition)

        StoreService.set_expire_all(session_key)

        self._resp.set_cookie(
            CDZSTAT_REQUEST_NUM_NAME,
            transition,
            expires=CDZSTAT_SESSION_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )

        self._resp.set_cookie(
            CDZSTAT_SESSION_COOKIE_NAME,
            session_key,
            expires=CDZSTAT_SESSION_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )

        """
        At the end send notification for the SessionWorker  
        """
        NotifyService.send_notify(CDZSTAT_QUEUE_SESSION, json.dumps({
            'from': 'low_level',
            CDZSTAT_SESSION_COOKIE_NAME: session_key,
            'transition': transition
        }))

    def _collect_data(self) -> dict:
        result = {
            'session': self._req.COOKIES.get(CDZSTAT_SESSION_COOKIE_NAME),
            'user_agent': self._req.META['HTTP_USER_AGENT'],
            'ip_address': utils.get_ip(self._req),
            'data_dynamic': {
                'status_code': self._resp.status_code,
                'response_time': time.time() - self._req.start_time
            },
            'navigate': {
                'host': self._req.META.get('HTTP_HOST'),
                'path': self._req.path,
                'referer': self._req.META.get('HTTP_REFERER') or '',
            }
        }

        return result


class HeightLevelService:

    def __init__(self, request):
        self._req = request

    def process(self):
        full_data = json.loads(self._req.body.decode())

        data = full_data.get('data')
        param = full_data.get('param')
        speed = full_data.get('speed')

        session_key = data.get('session_key')
        request_inc = data.get('request_inc')

        is_anonymous = not StoreService.session_exists(session_key)
        if is_anonymous:
            # ToDo anonymous
            pass

        StoreService.add_session_data(param, session_key)

        if request_inc:
            transition = StoreService.get_transition(session_key, request_inc)
            transition.update(speed)
            StoreService.update_transition(
                session_key, request_inc, transition
            )

        NotifyService.send_notify(CDZSTAT_QUEUE_SESSION, json.dumps({
            'from': 'height_level',
            CDZSTAT_SESSION_COOKIE_NAME: session_key,
            CDZSTAT_REQUEST_NUM_NAME: request_inc,
            'is_anonymous': is_anonymous
        }))


class DataHandlerService:

    def __init__(self, data):
        self._data = data

    def process(self):
        print(f'Process data with session key: {self._data}')
