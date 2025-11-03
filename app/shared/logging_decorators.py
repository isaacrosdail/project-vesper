import logging
from functools import wraps

def log_parser(func):
    """Logs input & output of parser functions"""
    @wraps(func)
    def wrapper(form_data):

        logger = logging.getLogger(func.__module__)
        logger.debug(f"{func.__name__} input: {form_data}")

        result = func(form_data)

        logger.debug(f"{func.__name__} output: {result}")
        return result
    return wrapper


def log_validator(func):
    """Logs validation attempts and errors"""
    @wraps(func)
    def wrapper(data):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"{func.__name__} validating: {data}")
        
        typed_data, errors = func(data)
        
        if errors:
            logger.warning(f"{func.__name__} validation failed: {errors}")
        else:
            logger.debug(f"{func.__name__} validation passed")
        
        return typed_data, errors
    return wrapper