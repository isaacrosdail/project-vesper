
from collections.abc import Callable
from functools import wraps
from typing import Any, Concatenate, ParamSpec, TypeVar

from flask.typing import ResponseReturnValue

from app._infra.database import database_connection
from app.modules.auth.service import typed_login_required

P = ParamSpec("P")
R = TypeVar("R")

type Data = dict[str, Any]
type Errors = dict[str, list[str]]
type Validator[T] = Callable[[dict[str, Any]], tuple[T | None, Errors]]


def login_plus_session(
    func: Callable[Concatenate[Any, P], ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]:
    """
    Combines `@login_required` and `@with_db_session` decorators.

    Ensures user is authenticated and passes a scoped DB session as first argument.
    """

    @wraps(func)
    @typed_login_required
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> ResponseReturnValue:
        with database_connection() as session:
            return func(session, *args, **kwargs)

    return decorated_function


# # TODO: Doublecheck - changing to align with dataclasses for validated results changes
# T = TypeVar("T")
# def log_validator(
#     func: Callable[P, tuple[T | None, Errors]]
# ) -> Callable[P, tuple[T | None, Errors]]:
#     """Logs validation attempts and errors"""

#     @wraps(func)
#     def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[T | None, Errors]:
#         logger = logging.getLogger(func.__module__)
#         logger.debug("%s validating: %s", func.__name__, args[0] if args else None)

#         result, errors = func(*args, **kwargs)
#         if errors:
#             logger.warning("%s validation failed: %s", func.__name__, errors)
#         else:
#             logger.debug("%s validation passed: %s", func.__name__, result)
#         return result, errors

#     return wrapper

