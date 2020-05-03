import uuid

from django.db import models

from . import EXCEPTION_TYPE, utils


class TimeZoneInfo(models.Model):
    name = models.CharField(max_length=64)
    abbr = models.CharField(max_length=8, verbose_name='abbreviation')
    offset = models.FloatField()
    isdst = models.BooleanField(verbose_name='Is Daylight Saving Time')
    text = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class TimeZone(models.Model):
    tz_info = models.ForeignKey(
        'TimeZoneInfo',
        on_delete=models.CASCADE,
        null=True
    )
    data = models.CharField(max_length=32)

    def __str__(self):
        return self.data


class ScreenSize(models.Model):
    height = models.IntegerField()
    width = models.IntegerField()

    def __str__(self):
        return f'H: {self.height}, W: {self.width}'


class WindowSize(models.Model):
    height = models.IntegerField()
    width = models.IntegerField()

    def __str__(self):
        return f'H: {self.height}, W: {self.width}'


class ColorParam(models.Model):
    color_depth = models.IntegerField()
    pixel_depth = models.IntegerField()

    def __str__(self):
        return f'Color: {self.color_depth}, Pixel: {self.pixel_depth}'


class UserLang(models.Model):
    data = models.CharField(max_length=8)

    def __str__(self):
        return self.data


class Browser(models.Model):
    data = models.CharField(max_length=128, db_index=True)
    version = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.data} {self.version}'


class Host(models.Model):
    id = models.AutoField(primary_key=True)
    dt_create = models.DateTimeField(auto_now_add=True)
    host = models.CharField(max_length=256, db_index=True)

    def __str__(self):
        return self.host


class IpAddress(models.Model):
    id = models.BigAutoField(primary_key=True)
    dt_create = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(db_index=True, unique=True)

    def __str__(self):
        return str(self.ip)


class UserAgent(models.Model):
    dt_create = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)
    data = models.TextField(db_index=True, unique=True)

    def __str__(self):
        return self.data[:50]


class SystemInfo(models.Model):
    dt_create = models.DateTimeField(auto_now_add=True)
    os_version = models.CharField(max_length=64, null=True, blank=True)
    platform = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f'OS: {self.os_version}, PLATF: {self.platform}'


class Path(models.Model):
    id = models.BigAutoField(primary_key=True)
    dt_create = models.DateTimeField(auto_now_add=True)
    host = models.ManyToManyField('Host')
    path = models.TextField(db_index=True)

    def __str__(self):
        return self.path[:100]


class ExternalReferer(models.Model):
    id = models.BigAutoField(primary_key=True)
    dt_create = models.DateTimeField(auto_now_add=True)
    data = models.TextField(db_index=True)

    def __str__(self):
        return self.data[:100]


class ExceptionPath(models.Model):
    dt_create = models.DateTimeField(
        auto_now_add=True
    )
    state = models.BooleanField(
        default=True
    )
    except_type = models.CharField(
        max_length=5,
        choices=EXCEPTION_TYPE,
        default='match'
    )
    host = models.ForeignKey(
        'Host',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    path = models.TextField(
        db_index=True
    )

    def __str__(self):
        return f'{self.host}{self.path}'


class Request(models.Model):
    class Meta:
        unique_together = ('session', 'key')

    id = models.BigAutoField(
        primary_key=True
    )
    key = models.CharField(
        max_length=10,
        default=utils.rand_symbols
    )
    dt_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date and Time create entry'
    )
    session = models.ForeignKey(
        'SessionData',
        on_delete=models.CASCADE,
        null=True
    )
    entry_point = models.BooleanField(
        default=False
    )
    host = models.ForeignKey(
        'Host',
        on_delete=models.CASCADE,
        null=True
    )
    path = models.ForeignKey(
        'Path',
        on_delete=models.CASCADE,
        null=True,
    )
    referer = models.ForeignKey(
        'Path',
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='referer'
    )
    external_referer = models.ForeignKey(
        'ExternalReferer',
        on_delete=models.DO_NOTHING,
        null=True
    )
    status_code = models.IntegerField()
    response_time = models.FloatField()
    processing_time = models.IntegerField(
        null=True,
        help_text='Measure in milliseconds. Start: domLoading End: domComplete'
    )
    loading = models.IntegerField(
        null=True,
        help_text='Measure in milliseconds. ' +
                  'Start: responseStart, End: responseEnd'
    )

    def __str__(self):
        return str(self.id)


class SessionData(models.Model):
    key = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid.uuid4,
        editable=False
    )
    dt_create = models.DateTimeField(
        auto_now_add=True
    )
    expire_date = models.DateTimeField()
    ip = models.ForeignKey(
        'IpAddress',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Ip address'
    )
    ua = models.ForeignKey(
        'UserAgent',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='User-Agent'
    )
    browser_lang = models.ForeignKey(
        'UserLang',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    time_zone = models.ForeignKey(
        'TimeZone',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    screen_size = models.ForeignKey(
        'ScreenSize',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    window_size = models.ForeignKey(
        'WindowSize',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    color_param = models.ForeignKey(
        'ColorParam',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    browser = models.ForeignKey(
        'Browser',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    system_info = models.ForeignKey(
        'SystemInfo',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.key
