import json
import re
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
)
from cdzstat import (
    models,
    handlers,
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


class StoreService:

    def __init__(self):
        pass

    @staticmethod
    def add_node(session: str, path: str, entry_point: bool = True):
        REDIS_CONN.hset(
            utils.get_node(session),
            path,
            json.dumps({
                'counter': 1,
                'entry_point': str(entry_point)
            })
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
    def add_edge(session: str, from_node: str, to_node: str):
        return REDIS_CONN.rpush(
            utils.get_edge(session),
            json.dumps({'from': from_node, 'to': to_node})
        )

    @staticmethod
    def add_adjacency(session: str, node: str, edge: int):
        edges = [edge]
        adjacency = REDIS_CONN.hget(utils.get_adjacency(session), node)
        if adjacency:
            adjacency = json.loads(adjacency)
            edges.extend(adjacency)
        return REDIS_CONN.hset(
            utils.get_adjacency(session),
            node,
            json.dumps(edges)
        )

    @staticmethod
    def set_expire_all(session):
        with REDIS_CONN.pipeline() as pipe:
            pipe.expire(utils.get_session(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_node(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_edge(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_adjacency(session), CDZSTAT_SESSION_AGE)
            pipe.execute()

    @staticmethod
    def to_json(session):
        session_data = REDIS_CONN.hgetall(utils.get_session(session))
        node_data = REDIS_CONN.hgetall(utils.get_node(session))
        edge_data = REDIS_CONN.lrange(utils.get_edge(session), 0, -1)
        adjacency_data = REDIS_CONN.hgetall(utils.get_adjacency(session))

        return json.dumps({
            'session': session_data,
            'node': node_data,
            'edge': edge_data,
            'adjacency': adjacency_data
        })


class LowLevelService:

    def __init__(self, request, response) -> None:
        self._req = request
        self._resp = response

    def process(self) -> None:
        session_key, data, navigate = self._collect_data()

        session_key = session_key[0]
        new_session = False

        current_path = navigate.get('path')
        current_referer = navigate.get('referer')
        referer = utils.split_url(current_referer)

        if not session_key:
            new_session = True
        else:
            skey = REDIS_CONN.hgetall(utils.get_session(session_key))
            if not skey:
                new_session = True
            else:
                StoreService.set_expire_all(session_key)

        if new_session:
            session_key = str(uuid4())
            with REDIS_CONN.pipeline() as pipe:
                for k, v in data.items():
                    pipe.hset(utils.get_session(session_key), k, v)
                pipe.execute()
                StoreService.set_expire_all(session_key)

        if StoreService.check_node(session_key, current_path):
            StoreService.inc_node(session_key, current_path)
        else:
            StoreService.add_node(
                session_key,
                current_path,
                ServiceUtils.check_entry_point(
                    referer['host'],
                    referer['path']
                )
            )

        edge = StoreService.add_edge(session_key, referer['path'], current_path)
        StoreService.add_adjacency(session_key, current_path, edge)

        self._resp.set_cookie(
            CDZSTAT_SESSION_COOKIE_NAME,
            session_key,
            expires=CDZSTAT_SESSION_AGE,
            path=settings.SESSION_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE or None,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )

    def _collect_data(self) -> (str, dict, dict):
        session = self._req.COOKIES.get(CDZSTAT_SESSION_COOKIE_NAME),
        data = {
            'ip_address': utils.get_ip(self._req),
            'user_agent': self._req.META['HTTP_USER_AGENT'],
            'status_code': self._resp.status_code
        }
        navigate = {
            'host': self._req.META.get('HTTP_HOST'),
            'path': self._req.path,
            'referer': self._req.META.get('HTTP_REFERER') or '',
        }
        return session, data, navigate


class HeightLevelService:

    def __init__(self, request):
        self._req = request

    def process(self):
        full_data = json.loads(self._req.body.decode())

        hlist = list()
        hlist.append(handlers.DataHandler)
        hlist.append(handlers.ParamHandler)

        hlist.sort(key=lambda x: x.priority)

        for handler in hlist:
            if handler.state:
                handler(full_data).process()
