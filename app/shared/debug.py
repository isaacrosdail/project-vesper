from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flask import Flask
    from app.config import BaseConfig

import sys
import logging.config

from flask import Flask, request
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ArgumentError
from werkzeug.serving import is_running_from_reloader

# ANSI Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def setup_dev_debugging(app: Flask) -> None:
    """
    Initialize extra debug output for dev, testing ENVs.
    """
    print_startup_info(app)
    setup_request_debugging(app)


def _safe_db_uri(uri: str) -> str:
    """Mask database password in debug output."""
    try:
        return make_url(uri).render_as_string(hide_password=True)
    except ArgumentError:
        return uri


def print_startup_info(app: Flask) -> None:
    """Print startup info once in the child process."""
    if not is_running_from_reloader():
        return

    logger = logging.getLogger(__name__)
    app_env = app.config.get("APP_ENV")
    debug = app.config.get("DEBUG")
    db = _safe_db_uri(app.config["SQLALCHEMY_DATABASE_URI"]).rsplit("/", 1)[1]

    # get actual log level (vs logger.level which doesn't check inheritance)
    log_level = logger.getEffectiveLevel()

    logger.debug(
        "[APP INIT] %s | DEBUG: %s | DB: %s | LOG LEVEL: %s",
        app_env,
        debug,
        db,
        log_level,
    )


def setup_request_debugging(app: 'Flask') -> None:
    """Set up request logging for dev environment"""

    @app.before_request
    def log_request() -> None:
        """Logs incoming request data (form data & query args) for debugging."""
        # Skip logging for CSS/JS files
        if '/static' in request.path:
            return

        logger = logging.getLogger(__name__)
        # Only log form data & args if they're not empty
        if request.form:
            logger.debug(f"Form data: {dict(request.form)}")
        if request.args:
            logger.debug(f"Query args: {dict(request.args)}")