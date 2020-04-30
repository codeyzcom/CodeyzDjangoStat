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

    def get_ctx(self):
        return self.ctx


class UserLanguageHandler(AbstractHandler):

    def __init__(self, request):
        super().__init__(request)

    def exec(self):
        lang = self._req.GET.get('user_lang')
        if lang:
            obj, created = models.UserLang.objects.get_or_create(data=lang)
            self.ctx['user_lang'] = obj


class TimezoneHandler(AbstractHandler):

    def exec(self):
        tz = self._req.GET.get('tz_info')
        if tz and tz != 'undefined':
            obj, created = models.TimeZone.objects.get_or_create(data=tz)
            self.ctx['time_zone'] = obj


class ScreenSizeHandler(AbstractHandler):

    def exec(self):
        height = self._req.GET.get('screen_height')
        width = self._req.GET.get('screen_width')
        if height and width:
            obj, created = models.ScreenSize.objects.get_or_create(
                height=height, width=width
            )
            self.ctx['screen_size'] = obj


class WindowSizeHandler(AbstractHandler):

    def exec(self):
        height = self._req.GET.get('window_height')
        width = self._req.GET.get('window_width')
        if height and width:
            obj, created = models.WindowSize.objects.get_or_create(
                height=height, width=width
            )
            self.ctx['window_size'] = obj


class ColorParamHandler(AbstractHandler):

    def exec(self):
        color = self._req.GET.get('screen_color_depth')
        pixel = self._req.GET.get('screen_pixel_depth')
        if color and pixel:
            obj, created = models.ColorParam.objects.get_or_create(
                color_depth=color,
                pixel_depth=pixel
            )
            self.ctx['color_param'] = obj


class BrowserHandler(AbstractHandler):

    def exec(self):
        browser = self._req.GET.get('browser')
        if browser:
            name, version = browser.split(' ')
            obj, created = models.Browser.objects.get_or_create(
                data=name,
                version=version
            )
            self.ctx['browser'] = obj


class SystemInfoHandler(AbstractHandler):

    def exec(self):
        platform = self._req.GET.get('platform')
        os_version = self._req.GET.get('os_version')
        if platform or os_version:
            obj, created = models.SystemInfo.objects.get_or_create(
                platform=platform,
                os_version=os_version
            )
            self.ctx['system_info'] = obj
            self.ctx['browser'] = obj


class SystemInfoHandler(AbstractHandler):

    def exec(self):
        platform = self._req.GET.get('platform')
        os_version = self._req.GET.get('os_version')
        if platform or os_version:
            obj, created = models.SystemInfo.objects.get_or_create(
                platform=platform,
                os_version=os_version
            )
            self.ctx['system_info'] = obj
