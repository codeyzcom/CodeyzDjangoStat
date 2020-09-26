from django.contrib import admin

from cdzstat import models


class TransitionInline(admin.TabularInline):
    model = models.Transition
    extra = 0
    can_delete = False
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'session', 'entry_point',
        'host', 'path', 'referer', 'external_referer', 'status_code',
        'response_time', 'processing_time', 'loading'
    )


@admin.register(models.Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'host')


@admin.register(models.Node)
class PathAdmin(admin.ModelAdmin):
    list_display = ('id', 'path')


@admin.register(models.IpAddress)
class IpAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip')
    search_fields = ('ip',)


@admin.register(models.UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'is_bot')
    search_fields = ('data',)
    list_filter = ('is_bot',)


@admin.register(models.Transition)
class TransitionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'path', 'status_code', 'response_time',
        'created_at', 'entry_point'
    )
    list_filter = ('status_code',)
    readonly_fields = (
        'id', 'created_at', 'session', 'entry_point', 'host', 'path',
        'referer', 'external_referer', 'status_code', 'response_time',
        'processing_time', 'loading'
    )


class ExceptionPathAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'path', 'state')


@admin.register(models.TimeZoneInfo)
class TimeZoneInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'offset', 'abbr', 'isdst')
    list_filter = ('isdst', 'offset')
    search_fields = ('name',)


@admin.register(models.TimeZone)
class TimeZoneAdmin(admin.ModelAdmin):
    list_display = ('data', 'tz_info')


@admin.register(models.ScreenSize)
class ScreenSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'width', 'height')


@admin.register(models.WindowSize)
class WindowSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'width', 'height')


@admin.register(models.ColorParam)
class ColorParamAdmin(admin.ModelAdmin):
    list_display = ('id', 'color_depth', 'pixel_depth')


@admin.register(models.UserLang)
class UserLangAdmin(admin.ModelAdmin):
    list_display = ('data',)


@admin.register(models.Browser)
class BrowserAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'version')


@admin.register(models.SystemInfo)
class SystemInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'platform', 'os_version')


@admin.register(models.SessionData)
class SessionDataAdmin(admin.ModelAdmin):
    list_display = ('key', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = (TransitionInline,)


@admin.register(models.ExternalReferer)
class ExternalRefererAdmin(admin.ModelAdmin):
    pass
