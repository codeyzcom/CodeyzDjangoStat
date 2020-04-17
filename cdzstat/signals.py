from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import (
    ExceptionPath,
    UserAgent,
)
from . import (
    USER_AGENT_CACHE,
    EXCEPTION_CACHE_DIRECT,
    EXCEPTION_CACHE_REGEX,
)


@receiver(post_save, sender=ExceptionPath)
def update_exception(*args, **kwargs):
    EXCEPTION_CACHE_DIRECT.clear()
    EXCEPTION_CACHE_REGEX.clear()


@receiver(post_save, sender=UserAgent)
def update_user_agent(*args, **kwargs):
    USER_AGENT_CACHE.clear()
