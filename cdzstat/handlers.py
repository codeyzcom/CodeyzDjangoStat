from abc import abstractmethod

from cdzstat import models


class AbstractHandler:
    priority = 100
    state = True
    ctx = dict()

    def __init__(self, request):
        self._req = request

    @abstractmethod
    def exec(self):
        pass


class UserLanguageHandler(AbstractHandler):

    def exec(self):
        lang = self._req.GET.get('user_lang')
        if lang:
            models.UserLang.objects.get_or_create(data=lang)


class TimezoneHandler(AbstractHandler):

    def exec(self):
        tz = self._req.GET.get('tz_info')
        if tz and tz != 'undefined':
            models.Utc.objects.get_or_create(data=tz)


class ScreenSizeHandler(AbstractHandler):

    def exec(self):
        height = self._req.GET.get('screen_height')
        width = self._req.GET.get('screen_width')
        if height and width:
            models.ScreenSize.objects.get_or_create(height=height, width=width)


class WindowSizeHandler(AbstractHandler):

    def exec(self):
        height = self._req.GET.get('window_height')
        width = self._req.GET.get('window_width')
        if height and width:
            models.WindowSize.objects.get_or_create(height=height, width=width)


class ColorParamHandler(AbstractHandler):

    def exec(self):
        color = self._req.GET.get('screen_color_depth')
        pixel = self._req.GET.get('screen_pixel_depth')
        if color and pixel:
            models.ColorParam.objects.get_or_create(
                color_depth=color,
                pixel_depth=pixel
            )


class BrowserHandler(AbstractHandler):

    def exec(self):
        browser = self._req.GET.get('browser')
        if browser:
            name, version = browser.split(' ')
            models.Browser.objects.get_or_create(
                data=name,
                version=version
            )
