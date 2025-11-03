import os
import sys
import logging.config

from flask import Flask, request
from sqlalchemy.engine.url import make_url

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(message)s",
        }
    },
    "handlers": { # dictates where logs go (console, file, etc.)
        "stdout": {
            "class": "logging.StreamHandler", # prints to console
            "formatter": "simple", # references formatter above
            "stream": "ext://sys.stderr", # ext:// means "external" ie "this is a variable that's defined outside of this config"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["stdout"]
    },
}

def setup_logging(app):
    """Configure logging based on app config"""
    print(f"Root level before: {logging.getLogger().level}", file=sys.stderr)
    config = LOGGING_CONFIG.copy()
    print(f"Config dict root level: {config['root']['level']}", file=sys.stderr)    
    config['root']['level'] = app.config['LOGGING_LEVEL']
    print(f"[setup_logging] Setting root to: {app.config['LOGGING_LEVEL']}", file=sys.stderr)
    print(f"Config dict after update: {config['root']['level']}", file=sys.stderr)
    
    logging.config.dictConfig(config=config)
    
    print(f"[AFTER setup_logging] Root level name: {logging.getLevelName(logging.getLogger().level)}", file=sys.stderr)


# Masks DB password in debug output
def safe_db_uri(uri: str) -> str:
    try:
        return make_url(uri).render_as_string(hide_password=True) # Displays DB password as **
    except Exception:
        return uri  # TODO: NOTES: non-SQLAlchemy URI?

def print_env_info(app: Flask):
    """ Print current env & config info for debugging """
    # Prevent repeated logging on every reload
    if getattr(app, "_config_logged", False):
        return
    
    logger = logging.getLogger(__name__)
    app_env = app.config.get('APP_ENV')
    debug = app.config.get('DEBUG')
    testing = app.config.get('TESTING')
    db = app.config.get('SQLALCHEMY_DATABASE_URI')
    logger.info(f"\n\nENVIRONMENT INFO")
    logger.info(f"APP_ENV: {app_env} | Debug: {debug} | Testing: {testing}")
    logger.info(f"Database: {safe_db_uri(db)}\n\n")

    app._config_logged = True # don't repeat on reload


def debug_config(config_name: str, config_class):
    """ Print which config is being loaded """
    logger = logging.getLogger(__name__)
    logger.info(f"\n[CONFIG] Loading {config_name} config: {config_class.__name__}")


def setup_request_debugging(app: Flask):
    """Set up request logging for dev environment"""

    @app.before_request
    def log_request():
        # Skip logging for CSS/JS files
        if '/static' in request.path:
            return

        logger = logging.getLogger(__name__)
        # Only log form data & args if they're not empty
        if request.form:
            logger.debug(f"Form data: {dict(request.form)}")
        if request.args:
            logger.debug(f"Query args: {dict(request.args)}")