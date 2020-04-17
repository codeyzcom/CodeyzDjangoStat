from django.db import models

from . import EXCEPTION_TYPE


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


class Path(models.Model):
    id = models.BigAutoField(primary_key=True)
    dt_create = models.DateTimeField(auto_now_add=True)
    host = models.ManyToManyField('Host')
    path = models.TextField(db_index=True)

    def __str__(self):
        return self.path[:50]


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
    id = models.BigAutoField(
        primary_key=True
    )
    dt_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date and Time create entry'
    )
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
    host = models.ForeignKey(
        'Host',
        on_delete=models.CASCADE,
        null=True
    )
    path = models.ForeignKey(
        'Path',
        on_delete=models.CASCADE,
        null=True
    )
    status_code = models.IntegerField()
    response_time = models.FloatField()
