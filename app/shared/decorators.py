import logging
from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec, Concatenate

P = ParamSpec("P")
R = TypeVar("R")

type Data = dict[str, Any]
type Errors = dict[str, list[str]]
type Validator = Callable[[Data], tuple[Data, Errors]]
type Parser = Callable[[Data], Data]

from flask_login import login_required

from app._infra.database import database_connection


# Decorator to combine login_required & with_db_session
def login_plus_session(f: Callable[Concatenate[Any, P], R]) -> Callable[P, R]:
    """Combines @login_required and @with_db_session decorators."""
    @wraps(f)
    @login_required  # type: ignore[misc]
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R:
        with database_connection() as session:
            return f(session, *args, **kwargs)
    return decorated_function


def log_parser(func: Parser) -> Parser:
    """Logs input & output of parser functions"""

    @wraps(func)
    def wrapper(form_data: Data) -> Data:
        logger = logging.getLogger(func.__module__)
        logger.debug("%s input: %s", func.__name__, form_data)

        result = func(form_data)
        logger.debug("%s output: %s", func.__name__, result)
        return result

    return wrapper


def log_validator(func: Validator) -> Validator:
    """Logs validation attempts and errors"""

    @wraps(func)
    def wrapper(data: Data) -> tuple[Data, Errors]:
        logger = logging.getLogger(func.__module__)
        logger.debug("%s validating: %s", func.__name__, data)

        typed_data, errors = func(data)
        if errors:
            logger.warning("%s validation failed: %s", func.__name__, errors)
        else:
            logger.debug("%s validation passed", func.__name__)
        return typed_data, errors
    return wrapper