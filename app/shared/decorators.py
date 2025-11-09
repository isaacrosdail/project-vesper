
import logging
from functools import wraps
from typing import Any, Callable

from flask_login import login_required

from app._infra.database import database_connection


# Decorator to combine login_required & with_db_session
def login_plus_session(f: Callable[..., Any]) -> Callable[..., Any]:
    """Combined decorator: requires login & injects db session"""
    @wraps(f)
    @login_required  # type: ignore[misc]
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        with database_connection() as session:
            return f(session, *args, **kwargs)
    return decorated_function


def log_parser(f: Callable[..., Any]) -> Callable[..., Any]:
    """Logs input & output of parser ftions"""
    @wraps(f)
    def wrapper(form_data: Any) -> Any:
        logger = logging.getLogger(f.__module__)
        logger.debug(f"{f.__name__} input: {form_data}")

        result = f(form_data)
        logger.debug(f"{f.__name__} output: {result}")
        return result
    return wrapper


def log_validator(f: Callable[..., Any]) -> Callable[..., Any]:
    """Logs validation attempts and errors"""
    @wraps(f)
    def wrapper(data: Any) -> Any:
        logger = logging.getLogger(f.__module__)
        logger.debug(f"{f.__name__} validating: {data}")
        
        typed_data, errors = f(data)
        if errors:
            logger.warning(f"{f.__name__} validation failed: {errors}")
        else:
            logger.debug(f"{f.__name__} validation passed")
        return typed_data, errors
    return wrapper