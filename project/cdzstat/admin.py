from django.contrib import admin

from .models import (
    Host,
    ExceptionPath
)


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'host')


@admin.register(ExceptionPath)
class ExceptionPathAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'path', 'state')
