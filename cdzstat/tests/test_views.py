from unittest import mock

from django.test import (
    TestCase,
    RequestFactory,
)

from cdzstat import views


class CollectorTest(TestCase):

    def setUp(self) -> None:
        self.req_post = RequestFactory().post('/')

    @mock.patch('cdzstat.views.HeightLevelService')
    def test_post(self, p_height_lvl_srv):
        result = views.collector(self.req_post)
        p_height_lvl_srv.assert_called_once()
        self.assertEqual(result.status_code, 204)
