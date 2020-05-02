from django.test import (
    TestCase,
    RequestFactory,
)

from cdzstat import (
    handlers,
    models,
)


class AbstractHandlerTest(TestCase):

    def setUp(self) -> None:
        self.req = RequestFactory().get('/')

    def test_exec(self):
        abs_hnd = handlers.AbstractHandler(request=self.req)
        result = abs_hnd.exec()
        self.assertIsNone(result)


class UserLanguageHandlerTest(TestCase):

    def setUp(self) -> None:
        self.req = RequestFactory().get('/?user_lang=en-US')
        self.req_err = RequestFactory().get('/?user_lang=')

    def test_exec_error(self):
        usr_lang_hnd = handlers.UserLanguageHandler(request=self.req_err)
        result = usr_lang_hnd.exec()
        self.assertIsNone(result)

    def test_exec(self):
        usr_lang_hnd = handlers.UserLanguageHandler(request=self.req)
        usr_lang_hnd.exec()
        usr_lang_obj = models.UserLang.objects.get(data='en-US')
        self.assertEqual(usr_lang_obj.data, 'en-US')


class TimezoneHandlerTest(TestCase):

    def setUp(self) -> None:
        self.req = RequestFactory().get('/?tz_info=America/Phoenix')
        self.req_err = RequestFactory().get('/?tz_info=undefined')

    def test_exec_error(self):
        tz_hnd = handlers.TimezoneHandler(request=self.req_err)
        result = tz_hnd.exec()
        self.assertIsNone(result)

    def test_exec(self):
        tz_hnd = handlers.TimezoneHandler(request=self.req)
        result = tz_hnd.exec()
        tz_obj = models.TimeZone.objects.get(data='America/Phoenix')
        self.assertEqual(tz_obj.data, 'America/Phoenix')
        self.assertIsNone(result)


class ScreenSizeHandlerTest(TestCase):

    def setUp(self) -> None:
        self.req = RequestFactory().get('/?screen_height=760&screen_width=360')
        self.req_err = RequestFactory().get('/?screen_height=&screen_width=36')

    def test_exec_error(self):
        size_hnd = handlers.ScreenSizeHandler(request=self.req_err)
        result = size_hnd.exec()
        self.assertIsNone(result)

    def test_exec(self):
        size_hnd = handlers.ScreenSizeHandler(request=self.req)
        result = size_hnd.exec()
        size_obj = models.ScreenSize.objects.all()
        self.assertEqual(size_obj[0].height, 760)
        self.assertEqual(size_obj[0].width, 360)
        self.assertIsNone(result)


class WindowSizeHandlerTeset(TestCase):

    def setUp(self) -> None:
        self.req = RequestFactory().get('/?window_height=980&window_width=360')
        self.req_err = RequestFactory().get('/?window_height=&window_width=')

    def test_exec_error(self):
        wnd_hnd = handlers.WindowSizeHandler(request=self.req_err)
        result = wnd_hnd.exec()
        self.assertIsNone(result)

    def test_exec(self):
        wnd_hnd = handlers.WindowSizeHandler(request=self.req)
        result = wnd_hnd.exec()
        size_obj = models.WindowSize.objects.all()
        self.assertEqual(size_obj[0].height, 980)
        self.assertEqual(size_obj[0].width, 360)
        self.assertIsNone(result)


class ColorParamHandlerTest(TestCase):

    def setUp(self) -> None:
        self.req = RequestFactory().get(
            '/?screen_color_depth=24&screen_pixel_depth=24'
        )
        self.req_err = RequestFactory().get('/')

    def test_exec_error(self):
        color_hnd = handlers.ColorParamHandler(request=self.req_err)
        result = color_hnd.exec()
        self.assertIsNone(result)

    def test_exec(self):
        color_hnd = handlers.ColorParamHandler(request=self.req)
        result = color_hnd.exec()
        color_obj = models.ColorParam.objects.all()
        self.assertEqual(color_obj[0].color_depth, 24)
        self.assertEqual(color_obj[0].pixel_depth, 24)
        self.assertIsNone(result)


class BrowserHandlerTest(TestCase):

    def setUp(self) -> None:
        self.req = RequestFactory().get('/?browser=Chrome+81.0.4044.122')
        self.req_err = RequestFactory().get('/')

    def test_exec_error(self):
        browser_hnd = handlers.BrowserHandler(request=self.req_err)
        result = browser_hnd.exec()
        self.assertIsNone(result)

    def test_exec(self):
        browser_hnd = handlers.BrowserHandler(request=self.req)
        result = browser_hnd.exec()
        browser_obj = models.Browser.objects.all()
        self.assertEqual(browser_obj[0].data, 'Chrome')
        self.assertEqual(browser_obj[0].version, '81.0.4044.122')
        self.assertIsNone(result)
