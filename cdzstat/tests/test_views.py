from unittest import mock

from django.test import TestCase

from cdzstat import views


class CollectorTest(TestCase):

    @mock.patch('cdzstat.views.HeightLevelService')
    def test_collector(self, p_height_lvl_srv):
        result = views.collector(mock.Mock())
        p_height_lvl_srv.assert_called_once()
        self.assertEqual(result.status_code, 204)
