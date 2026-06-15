
import logging
import os
from collections.abc import Callable
from functools import wraps
from typing import Any, Concatenate, ParamSpec, TypeVar

from flask import abort, current_app, request
from flask.typing import ResponseReturnValue
from flask_login import current_user
from sqlalchemy import event

from app._infra.database import database_connection

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


def owner_required(
    func: Callable[P, ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]:
    """
    Decorator that ensures current_user is authenticaed and has OWNER role.

    Returns 403 Forbidden if user lacks owner permissions.
    """

    @wraps(func)
    @typed_login_required
    def decorated_view(*args: P.args, **kwargs: P.kwargs) -> ResponseReturnValue:
        if not current_user.is_owner:
            return abort(403, description="Owner privileges required")
        return func(*args, **kwargs)

    return decorated_view


EXEMPT_METHODS = {"OPTIONS"}  # copied from Flask-Login's source

def typed_login_required(
    func: Callable[P, ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]:
    """
    Typed version of Flask-Login's `login_required`.
    """

    @wraps(func)
    def decorated_view(*args: P.args, **kwargs: P.kwargs) -> ResponseReturnValue:
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()  # type: ignore[no-any-return, attr-defined]

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)  # type: ignore[no-any-return]
        return func(*args, **kwargs)

    return decorated_view


# Decorator factory to log queries in dev mode only
def log_queries(mode: str = "dev") -> Callable[[Callable[Concatenate[Any, P], R]], Callable[Concatenate[Any, P], R]]:
    def decorator(func: Callable[Concatenate[Any, P], R]) -> Callable[Concatenate[Any, P], R]:
        if os.environ.get("APP_ENV") != mode:
            return func # skip

        @wraps(func)
        def wrapper(repo: Any, /, *args: P.args, **kwargs: P.kwargs) -> R:
            logger = logging.getLogger(func.__module__)
            count = 0

            def increment(conn: Any, cursor: Any, statement: Any, parameters: Any, context: Any, executemany: Any) -> None:
                nonlocal count
                count += 1

            ## before: start counting queries
            # args[0] is self (the repo instance) which has self.session
            # args[0] -> repo
            connection = repo.session.connection()
            event.listen(connection, "before_cursor_execute", increment)

            # Try/finally: Need to clean up listener if repo method raises
            try:
                result = func(repo, *args, **kwargs)
            finally:
                ## after: stop counting, log the stats
                event.remove(connection, "before_cursor_execute", increment)
                logger.debug("%s.%s | queries: %d", repo.model_cls.__name__, func.__name__, count)

            return result
        return wrapper
    return decorator
