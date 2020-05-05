import random
import string


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rand_symbols(length: int = 10):
    return ''.join(
        random.choice(
            string.ascii_lowercase + string.digits
        ) for _ in range(length)
    )


def get_session(key):
    return f'session:{key}'


def get_navigation(key):
    return f'navigation:{key}'
