from django.test import TestCase

from cdzstat import models


class TimeZoneTest(TestCase):

    def setUp(self) -> None:
        self.tz = models.TimeZone.objects.filter(name__exact='UTC').first()

    def test_str(self):
        self.assertEqual(str(self.tz), 'UTC')


class UtcTest(TestCase):

    def setUp(self) -> None:
        self.utc = models.Utc.objects.filter(data='Europe/London').first()

    def test_str(self):
        self.assertEqual(str(self.utc), 'Europe/London')


class ScreenSizeTest(TestCase):

    def setUp(self) -> None:
        self.screen = models.ScreenSize.objects.create(height=768, width=1024)

    def test_str(self):
        self.assertEqual(str(self.screen), 'H: 768, W: 1024')


class WindowSizeTest(TestCase):

    def setUp(self) -> None:
        self.window = models.WindowSize.objects.create(height=768, width=1024)

    def test_str(self):
        self.assertEqual(str(self.window), 'H: 768, W: 1024')


class ColorParamTest(TestCase):

    def setUp(self) -> None:
        self.color = models.ColorParam.objects.create(
            color_depth=24, pixel_depth=24
        )

    def test_str(self):
        self.assertEqual(str(self.color), 'Color: 24, Pixel: 24')


class PlatformTest(TestCase):

    def setUp(self) -> None:
        self.platform = models.Platform.objects.create(data='Linux')

    def test_str(self):
        self.assertEqual(str(self.platform), 'Linux')


class UserLangTest(TestCase):

    def setUp(self) -> None:
        self.ua = models.UserLang.objects.create(data='en')

    def test_str(self):
        self.assertEqual(str(self.ua), 'en')


class HostTest(TestCase):

    def setUp(self) -> None:
        self.host = models.Host.objects.create(host='https://codeyz.com/')

    def test_str(self):
        self.assertEqual(str(self.host), 'https://codeyz.com/')


class IpAddressTest(TestCase):

    def setUp(self) -> None:
        self.ip_address = models.IpAddress.objects.create(ip='127.0.0.1')

    def test_str(self):
        self.assertEqual(str(self.ip_address), '127.0.0.1')


class UserAgentTest(TestCase):

    def setUp(self) -> None:
        self.ua = models.UserAgent.objects.create(
            is_bot=True,
            data='Mozilla 5.0'
        )

    def test_str(self):
        self.assertEqual(str(self.ua), 'Mozilla 5.0')


class PathTest(TestCase):

    def setUp(self) -> None:
        self.path = models.Path.objects.create(path='/page/1')

    def test_str(self):
        self.assertEqual(str(self.path), '/page/1')


class ExceptionPathTest(TestCase):

    def setUp(self) -> None:
        host = models.Host.objects.create(host='https://codeyz.com/')
        path = models.Path.objects.create(path='cdzstat/')
        self.exc = models.ExceptionPath.objects.create(host=host, path=path)

    def test_str(self):
        self.assertEqual(str(self.exc), 'https://codeyz.com/cdzstat/')
