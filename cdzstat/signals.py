from django.dispatch import receiver
from django.db.models.signals import post_save

from cdzstat.models import UserAgent
from cdzstat import (
    USER_AGENT_CACHE,
    EXCEPTION_CACHE_DIRECT,
    EXCEPTION_CACHE_REGEX, 
)


@receiver(post_save, sender=UserAgent)
def update_user_agent(*args, **kwargs):
    USER_AGENT_CACHE.clear()
