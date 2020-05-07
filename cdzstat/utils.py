import random
import string
from urllib.parse import urlparse

from django.utils.timezone import localtime


def get_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def split_url(url: str) -> dict:
    full = urlparse(url)
    return {'host': full.netloc, 'path': full.path}


def rand_symbols(length: int = 10) -> str:
    return ''.join(
        random.choice(
            string.ascii_lowercase + string.digits
        ) for _ in range(length)
    )


def get_dt():
    return localtime().today()


def get_session(key: str) -> str:
    return f'session:{key}'


def get_navigation(key: str) -> str:
    return f'navigation:{key}'


def get_node(key: str) -> str:
    return f'node:{key}'


def get_edge(key: str) -> str:
    return f'edge:{key}'


def get_adjacency(key: str) -> str:
    return f'adjacency:{key}'


def get_static(key: str) -> str:
    return f'static:{key}'
