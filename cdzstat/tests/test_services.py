import json
from unittest import mock

from django.test import TestCase

from cdzstat import services, models, utils, REDIS_CONN


class ServiceUtilsTest(TestCase):

    def setUp(self) -> None:
        models.Host.objects.create(host='127.0.0.1:8000')
        services.ServiceUtils.initialize_data()
        self.srv_utils = services.ServiceUtils()

    def tearDown(self) -> None:
        REDIS_CONN.flushall()

    def test_init(self):
        self.assertIsNone(self.srv_utils.__init__())

    def test_check_entry_point_false(self):
        ep = services.ServiceUtils.check_entry_point('127.0.0.1:8000', '/')
        self.assertFalse(ep)

    def test_check_entry_point_empty_path(self):
        ep = services.ServiceUtils.check_entry_point('127.0.0.1:8000', '')
        self.assertTrue(ep)

    def test_check_entry_point_true(self):
        ep = services.ServiceUtils.check_entry_point('example.com', '/')
        self.assertTrue(ep)


class StoreServiceTest(TestCase):

    def setUp(self) -> None:
        REDIS_CONN.flushall()
        self.session_key = '111-222-333'
        services.StoreService.add_session_data({'A': 'B'}, '111-222-333')

    def tearDown(self) -> None:
        REDIS_CONN.flushall()

    @mock.patch('cdzstat.services.uuid4')
    def test_add_session_data_session(self, p_uuid4):
        skey = '111'
        result = services.StoreService.add_session_data({'a': 'b'}, skey)
        res_obj = REDIS_CONN.hgetall(utils.get_session(skey))
        p_uuid4.assert_not_called()
        self.assertEqual(res_obj, {'a': 'b'})
        self.assertEqual(result, skey)

    @mock.patch('cdzstat.services.uuid4', return_value='111')
    def test_add_session_data_session_is_none(self, p_uuid4):
        skey = '111'
        result = services.StoreService.add_session_data({'a': 'b'})
        result_obj = REDIS_CONN.hgetall(utils.get_session(skey))
        p_uuid4.assert_called_once()
        self.assertEqual(result_obj, {'a': 'b'})
        self.assertEqual(result, skey)

    def test_session_exists_true(self):
        result = services.StoreService.session_exists(self.session_key)
        self.assertTrue(result)

    def test_session_exists_session_is_none(self):
        result = services.StoreService.session_exists(None)
        self.assertFalse(result)

    def test_session_exists_false(self):
        result = services.StoreService.session_exists('55555')
        self.assertFalse(result)

    @mock.patch(
        'cdzstat.services.utils.get_dt',
        return_value='2020-05-08 00:52:15.718827'
    )
    def test_add_node(self, p_dt_create):
        services.StoreService.add_node(self.session_key, '/')
        result = REDIS_CONN.hgetall(utils.get_node(self.session_key))
        p_dt_create.assert_called_once()
        self.assertEqual(
            result,
            {'/': '{"dt_create": "2020-05-08 00:52:15.718827", "counter": 1}'}
        )

    def test_inc_node(self):
        services.StoreService.add_node(self.session_key, '/index')
        services.StoreService.inc_node(self.session_key, '/index')
        result = REDIS_CONN.hget(utils.get_node(self.session_key), '/index')
        result = json.loads(result)
        self.assertEqual(result.get('counter'), 2)

    def test_check_node(self):
        services.StoreService.add_node(self.session_key, '/index')
        result = services.StoreService.check_node(self.session_key, '/index')
        self.assertTrue(result)

    @mock.patch(
        'cdzstat.services.utils.get_dt',
        return_value='2020-05-08 01:16:40.554194'
    )
    def test_add_edge(self, p_get_dt):
        services.StoreService.add_edge(self.session_key, '/index', '/page')
        result = REDIS_CONN.lindex(utils.get_edge(self.session_key), 0)
        p_get_dt.assert_called_once()
        self.assertEqual(
            result,
            '{"from": "/index", "to": "/page", ' +
            '"dt_create": "2020-05-08 01:16:40.554194"}'
        )
