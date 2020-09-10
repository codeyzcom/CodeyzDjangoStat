import random
import string
from urllib.parse import urlparse

from django.utils.timezone import localtime


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


def get_transition(key: str) -> str:
    return f'transition:{key}'


def get_adjacency(key: str) -> str:
    return f'adjacency:{key}'


def get_static(key: str) -> str:
    return f'static:{key}'


def get_ip_address(key):
    return f'ip_address:{key}'
