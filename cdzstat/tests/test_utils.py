from django.test import (
    TestCase,
    RequestFactory,
)

from cdzstat import utils


class GetIpTest(TestCase):

    def setUp(self) -> None:
        self.req = RequestFactory().get('/')

    def test_first_case(self):
        self.req.META['HTTP_X_FORWARDED_FOR'] = '10.10.10.10'
        result = utils.get_ip(self.req)
        self.assertEqual(result, '10.10.10.10')

    def test_second_case(self):
        result = utils.get_ip(self.req)
        self.assertEqual(result, '127.0.0.1')
