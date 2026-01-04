
import logging
from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec, Concatenate

P = ParamSpec("P")
R = TypeVar('R')

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


def log_parser(f: Parser) -> Parser:
    """Logs input & output of parser functions"""
    @wraps(f)
    def wrapper(form_data: Data) -> Data:
        logger = logging.getLogger(f.__module__)
        logger.debug(f"{f.__name__} input: {form_data}")

        result = f(form_data)
        logger.debug(f"{f.__name__} output: {result}")
        return result
    return wrapper


def log_validator(f: Validator) -> Validator:
    """Logs validation attempts and errors"""
    @wraps(f)
    def wrapper(data: Data) -> tuple[Data, Errors]:
        logger = logging.getLogger(f.__module__)
        logger.debug(f"{f.__name__} validating: {data}")
        
        typed_data, errors = f(data)
        if errors:
            logger.warning(f"{f.__name__} validation failed: {errors}")
        else:
            logger.debug(f"{f.__name__} validation passed")
        return typed_data, errors
    return wrapper