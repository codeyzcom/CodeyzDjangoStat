from django.contrib import admin

from cdzstat import models


@admin.register(models.Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'host')


@admin.register(models.Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ('id', 'path')


@admin.register(models.IpAddress)
class IpAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'dt_create')
    search_fields = ('ip',)


@admin.register(models.UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'is_bot')
    search_fields = ('data',)
    list_filter = ('is_bot',)


@admin.register(models.Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'path', 'ip', 'status_code', 'response_time', 'dt_create'
    )
    search_fields = ('ip__ip',)
    list_filter = ('status_code',)
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


@admin.register(models.ExceptionPath)
class ExceptionPathAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'path', 'state')


@admin.register(models.TimeZone)
class TimeZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'offset', 'abbr', 'isdst')
    list_filter = ('isdst', 'offset')
    search_fields = ('name',)


@admin.register(models.Utc)
class UtcAdmin(admin.ModelAdmin):
    list_display = ('data', 'time_zone')


@admin.register(models.ScreenSize)
class ScreenSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'height', 'width')


@admin.register(models.WindowSize)
class WindowSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'height', 'width')


@admin.register(models.ColorParam)
class ColorParamAdmin(admin.ModelAdmin):
    list_display = ('color_depth', 'pixel_depth')


@admin.register(models.Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('data',)


@admin.register(models.UserLang)
class UserLangAdmin(admin.ModelAdmin):
    list_display = ('data',)


@admin.register(models.Browser)
class BrowserAdmin(admin.ModelAdmin):
    list_display = ('data',)
