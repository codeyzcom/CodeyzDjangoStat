from django.contrib import admin

from .models import (
    Host,
    Path,
    Request,
    IpAddress,
    UserAgent,
    ExceptionPath
)


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'host')


@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ('id', 'path')


@admin.register(IpAddress)
class IpAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'dt_create')


@admin.register(UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'is_bot')
    search_fields = ('data',)
    list_filter = ('is_bot',)


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'path', 'ip', 'status_code', 'response_time')
    list_filter = ('status_code', )
    readonly_fields = (
        'id',
        'dt_create',
        'ip',
        'ua',
        'host',
        'path',
        'status_code',
        'response_time'
    )


@admin.register(ExceptionPath)
class ExceptionPathAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'path', 'state')
