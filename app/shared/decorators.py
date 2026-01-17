import logging
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
type Validator = Callable[[Data], tuple[Data, Errors]]
type Parser = Callable[[Data], Data]


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
