
import logging
import os
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from sqlalchemy import event

P = ParamSpec("P")
R = TypeVar("R")

# Usage:
# On a given repo method:
# @log_queries()   <- defaults to 'dev' ofc
# def my_repo_method(...):
#   ...

## TODO study: Parentheses are needed - without them, Python passes the function as the mode arg
# instead of as the thing to decorate.
# That's the factory layer thing: @log_queries() calls factory first, @log_queries skips it

def log_queries(mode="dev"):
    def decorator(func):
        if os.environ.get("APP_ENV") != mode:
            return func # skip

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            count = 0

            def increment(conn, cursor, statement, parameters, context, executemany):
                logger.debug("test")
                nonlocal count
                count += 1

            ## before: start counting queries
            # args[0] is self (the repo instance) which has self.session
            connection = args[0].session.connection()
            event.listen(connection, "before_cursor_execute", increment)

            # Try/finally here because if the repo method throws, we wanna clean up the listener still
            try:
                result = func(*args, **kwargs)
            finally:
                ## after: stop counting, log the stats
                event.remove(connection, "before_cursor_execute", increment)
                logger.debug("%s.%s | queries: %d", args[0].model_cls.__name__, func.__name__, count)

            return result ## return what the repo method returned
        return wrapper
    return decorator