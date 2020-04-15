from django.conf import settings

def get(key, default):
    return getattr(settings, key, default)
