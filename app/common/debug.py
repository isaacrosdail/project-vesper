import os
import sys

from flask import Flask, request, current_app, has_app_context
from sqlalchemy.engine.url import make_url

# TODO: Using stderr since Flask buffers print output, but there is undoubtedly a better way to do this.
def log_info(msg: str) -> None:
    if has_app_context():
        current_app.logger.info(msg)
    else:
        print(msg, file=sys.stderr, flush=True) # flush avoids buffering?

# Masks DB password in debug output
def safe_db_uri(uri: str) -> str:
    try:
        return make_url(uri).render_as_string(hide_password=True) # Displays DB password as **
    except Exception:
        return uri  # TODO: non-SQLAlchemy URI?

def print_env_info(app: Flask = None):
    """ Print current env & config info for debugging """
    log_info("\n" + "="*20)
    log_info("ENVIRONMENT DEBUG INFO")
    log_info("="*20)

    if app:
        log_info(f"APP_ENV (config): {app.config.get('APP_ENV', "Not set")}")
    log_info(f"APP_ENV (env var): {os.environ.get('APP_ENV', "Not set (default: dev)")}")
    log_info(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")

    # Flask app config
    if app:
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        log_info(f"\nActive Config: {app.config.get('ENV', 'Not set')}")
        log_info(f"DEBUG mode: {app.config.get('DEBUG', False)}")
        log_info(f"TESTING mode: {app.config.get('TESTING', False)}")
        log_info(f"Database URI: {safe_db_uri(db_uri)}")

    log_info("="*20 + "\n")

def debug_config(config_name: str, config_class):
    """ Print which config is being loaded """
    log_info(f"\n[CONFIG] Loading {config_name} config: {config_class.__name__}")


def request_debugging(app: Flask = None):
    @app.before_request
    def debug_everything():
        if request.endpoint == 'static':
            return # skip logging for CSS/JS files
        log_info("\n== REQUEST DEBUG ==")
        log_info(f"URL: {request.url}")
        log_info(f"Method: {request.method}")
        log_info(f"Endpoint: {request.endpoint}")
        log_info(f"Form data: {dict(request.form)}")
        log_info(f"Args: {dict(request.args)}")
        log_info("====================\n")