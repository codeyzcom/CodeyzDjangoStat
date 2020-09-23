import json
import time
from uuid import uuid4

from django.conf import settings

from cdzstat import REDIS_CONN
from cdzstat.settings import (
    CDZSTAT_SESSION_COOKIE_NAME,
    CDZSTAT_SESSION_AGE,
    CDZSTAT_REQUEST_NUM_NAME,
    CDZSTAT_QUEUE_SESSION,
    CDZSTAT_PERMANENT_COOKIE_NAME,
    CDZSTAT_PERMANENT_COOKIE_AGE,
)
from cdzstat import (
    models,
    utils,
    registry,
)


class SessionGarbageCollectorService:

    def __init__(self):
        pass
    
    def execute(self):
        reg = registry.SessionRegistry(REDIS_CONN)
        expired_keys = reg.get_expired_keys()

        if expired_keys:
            with REDIS_CONN.pipeline() as p:
                for key in expired_keys:
                    print(f'Notify about removing key {key}')
                    reg.remove(key, p)
                    p.delete(f'session:{key}')
                p.execute()



class ServiceUtils:

    def __init__(self):
        pass

    @staticmethod
    def initialize_application():
        REDIS_CONN.ping()

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
    def get_session_all(session: str) -> dict:
        return REDIS_CONN.hgetall(utils.get_session(session))

    @staticmethod
    def get_session_key(session: str, key: str) -> str:
        return REDIS_CONN.hget(session, key)

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
    def add_ip_address(session: str, ip: str, transition: int):
        transitions = [transition]
        ip_address = REDIS_CONN.hget(utils.get_ip_address(session), ip)
        if ip_address:
            exists_data = json.loads(ip_address)
            transitions.extend(exists_data)
        REDIS_CONN.hset(
            utils.get_ip_address(session), ip, json.dumps(transitions)
        )

    @staticmethod
    def set_expire_all(session: str) -> None:
        with REDIS_CONN.pipeline() as pipe:
            pipe.expire(utils.get_session(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_node(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_transition(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_adjacency(session), CDZSTAT_SESSION_AGE)
            pipe.expire(utils.get_ip_address(session), CDZSTAT_SESSION_AGE)
            pipe.execute()

    @staticmethod
    def to_json(session):
        session_data = REDIS_CONN.hgetall(utils.get_session(session))
        node_data = REDIS_CONN.hgetall(utils.get_node(session))
        adjacency_data = REDIS_CONN.hgetall(utils.get_adjacency(session))
        ip_address = REDIS_CONN.hgetall(utils.get_ip_address(session))
        transition_data = REDIS_CONN.lrange(
            utils.get_transition(session), 0, -1)

        return json.dumps({
            'session': session_data,
            'node': node_data,
            'transition': transition_data,
            'adjacency': adjacency_data,
            'ip_address': ip_address,
        })


class LowLevelService:

    def __init__(self, request, response) -> None:
        self._req = request
        self._resp = response

    def process(self) -> None:
        collected_data = self._collect_data()

        navigate = collected_data.get('navigate')
        d_data = collected_data.get('data_dynamic')

        permanent_key = collected_data.get('permanent')
        new_permanent = False

        session_key = collected_data.get('session')
        new_session = False

        current_host = navigate.get('host')
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
        Checking - if the permananet key exists in cookies and add the 
        data store
        """
        if not permanent_key:
            new_permanent = True
            permanent_key = str(uuid4())

        StoreService.add_session_data(
            {CDZSTAT_PERMANENT_COOKIE_NAME: permanent_key}, session_key
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
        Each time add information about adjacency to the data store
        """
        StoreService.add_adjacency(session_key, current_path, transition)

        """
        Each time add information about ip address to the data store
        """
        StoreService.add_ip_address(
            session_key, collected_data.get('ip_address'), transition
        )

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

        if new_permanent:
            self._resp.set_cookie(
                CDZSTAT_PERMANENT_COOKIE_NAME,
                permanent_key,
                expires=CDZSTAT_PERMANENT_COOKIE_AGE,
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
            'host': current_host,
            'node': current_path,
            'transition': transition
        }))

    def _collect_data(self) -> dict:
        result = {
            'session': self._req.COOKIES.get(CDZSTAT_SESSION_COOKIE_NAME),
            'permanent': self._req.COOKIES.get(CDZSTAT_PERMANENT_COOKIE_NAME),
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
    """
    Service called when received request from cdz_stat.js and it processes
    the received information by storing it in data store
    """

    def __init__(self, request):
        self._req = request

    def process(self):
        full_data = json.loads(self._req.body.decode())

        data = full_data.get('data')
        param = full_data.get('param')
        speed = full_data.get('speed')

        session_key = data.get('session_key')
        request_inc = data.get('request_inc')

        mutable_params = {
            'screen_height': param.pop('screen_height'),
            'screen_width': param.pop('screen_width'),
            'window_height': param.pop('window_height'),
            'window_width': param.pop('window_width'),
            'screen_color_depth': param.pop('screen_color_depth'),
            'screen_pixel_depth': param.pop('screen_pixel_depth')
        }

        is_anonymous = not StoreService.session_exists(session_key)
        if is_anonymous:
            # ToDo anonymous
            pass

        StoreService.add_session_data(param, session_key)

        """
        If we get the request id from the cookie, then we update the
        information in the data store using the session key
        """
        if request_inc:
            transition = StoreService.get_transition(session_key, request_inc)
            transition.update(speed)
            transition.update(mutable_params)
            StoreService.update_transition(
                session_key, request_inc, transition
            )

        """
        At the end send notification for the SessionWorker  
        """
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
        data = json.loads(self._data)
        from_level = data.get('from')
        session_key = data.get(CDZSTAT_SESSION_COOKIE_NAME)

        print(data)

        if from_level == 'low_level':
            DataHandlerService._low_level_handler(data)
        elif from_level == 'height_level':
            DataHandlerService._height_level_handler(session_key)

    @staticmethod
    def _low_level_handler(data):
        session_key = data.get(CDZSTAT_SESSION_COOKIE_NAME)
        host = data.get('host')
        node = data.get('node')
        transition = data.get('transition')

        transition_raw = StoreService.get_transition(session_key, transition)

        session_obj, created = models.SessionData.objects.get_or_create(
            key=session_key
        )

        host_obj, _ = models.Host.objects.get_or_create(host=host)

        node_obj, _ = models.Node.objects.get_or_create(path=node)
        node_obj.host.add(host_obj)
        node_obj.save()

        referer_obj, _ = models.Node.objects.get_or_create(
            path=transition_raw.get('from')
        )
        referer_obj.host.add(host_obj)
        referer_obj.save()

        if created:
            session_raw = StoreService.get_session_all(session_key)

            DataHandlerService._set_user_agent(
                session_key, session_raw.get('user_agent')
            )


    @staticmethod
    def _height_level_handler(session_key):

        session_raw = StoreService.get_session_all(session_key)
        DataHandlerService._set_user_lang(
            session_key, session_raw.get('user_lang')
        )

        DataHandlerService._set_timezone(
            session_key, session_raw.get('tz_info')
        )

        DataHandlerService._set_system_info(
            session_key,
            session_raw.get('platform'),
            session_raw.get('os_version')
        )

        DataHandlerService._set_browser(
            session_key,
            session_raw.get('browser')
        )

    @staticmethod
    def _set_user_agent(session: str, user_agent: str) -> None:
        ua, _ = models.UserAgent.objects.update_or_create(data=user_agent)
        models.SessionData.objects.filter(key=session).update(user_agent=ua)

    @staticmethod
    def _set_user_lang(session: str, user_lang: str) -> None:
        ul, _ = models.UserLang.objects.update_or_create(data=user_lang)
        models.SessionData.objects.filter(key=session).update(user_lang=ul)

    @staticmethod
    def _set_timezone(session: str, timezone):
        tz, _ = models.TimeZone.objects.update_or_create(data=timezone)
        models.SessionData.objects.filter(key=session).update(time_zone=tz)

    @staticmethod
    def _set_system_info(session: str, platform: str, os_version: str) -> None:
        si, _ = models.SystemInfo.objects.update_or_create(
            platform=platform, os_version=os_version
        )
        models.SessionData.objects.filter(key=session).update(system_info=si)

    @staticmethod
    def _set_browser(session: str, browser: str):
        br, _ = models.Browser.objects.update_or_create(data=browser)
        models.SessionData.objects.filter(key=session).update(browser=br)
