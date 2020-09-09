import uuid

from django.db import models

from . import EXCEPTION_TYPE, utils


class TimestampMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Время последнего изменения'
    )


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


class Browser(TimestampMixin):
    data = models.CharField(max_length=128, db_index=True)
    version = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.data} {self.version}'


class Host(TimestampMixin):
    host = models.CharField(max_length=256, db_index=True)

    def __str__(self):
        return self.host


class IpAddress(TimestampMixin):
    id = models.BigAutoField(primary_key=True)
    ip = models.GenericIPAddressField(db_index=True, unique=True)

    def __str__(self):
        return str(self.ip)


class UserAgent(TimestampMixin):
    is_bot = models.BooleanField(default=False)
    data = models.TextField(db_index=True, unique=True)

    def __str__(self):
        return self.data[:50]


class SystemInfo(TimestampMixin):
    os_version = models.CharField(max_length=64, null=True, blank=True)
    platform = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f'OS: {self.os_version}, PLATF: {self.platform}'


class ExternalReferer(TimestampMixin):
    id = models.BigAutoField(primary_key=True)
    data = models.TextField(db_index=True)

    def __str__(self):
        return self.data[:100]


class Node(TimestampMixin):
    id = models.BigAutoField(primary_key=True)
    host = models.ManyToManyField('Host')
    path = models.TextField(db_index=True)

    def __str__(self):
        return self.path[:100]


class Transition(TimestampMixin):
    class Meta:
        verbose_name = 'Transition'
        verbose_name_plural = 'Transitions'

    id = models.BigAutoField(
        primary_key=True
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
    referer = models.ForeignKey(
        'Node',
        on_delete=models.CASCADE,
        null=True,
        related_name='referer'
    )
    path = models.ForeignKey(
        'Node',
        on_delete=models.CASCADE,
        null=True,
    )
    external_referer = models.ForeignKey(
        'ExternalReferer',
        on_delete=models.DO_NOTHING,
        null=True
    )
    status_code = models.IntegerField(
        null=True,
        blank=True
    )
    response_time = models.FloatField(
        null=True,
        blank=True
    )
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



class Adjacency(TimestampMixin):
    o = models.IntegerField(
        verbose_name='Order'
    )
    session = models.ForeignKey(
        'SessionData',
        on_delete=models.CASCADE
    )
    node = models.ForeignKey(
        'Node',
        on_delete=models.CASCADE
    )
    transition = models.ManyToManyField(
        'Transition'
    )


class SessionData(TimestampMixin):
    key = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid.uuid4,
        editable=False
    )
    user_agent = models.ForeignKey(
        'UserAgent',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='User-Agent',
    )
    user_lang = models.ForeignKey(
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
    ip = models.ManyToManyField(
        'IpAddress',
        verbose_name='Ip address'
    )
    screen_size = models.ManyToManyField(
        'ScreenSize',
    )
    window_size = models.ManyToManyField(
        'WindowSize',
    )
    color_param = models.ForeignKey(
        'ColorParam',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.key

