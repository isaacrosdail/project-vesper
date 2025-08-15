## Trying out some more basic decorators
from functools import wraps

from flask import logging


def catch_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as exc:
            logging.error('Error: ' + str(exc))
    return decorated_function