import os
import sys

from flask import Flask, current_app, has_app_context, request
from sqlalchemy.engine.url import make_url


def should_debug_log(app):
    """Check if we should enable debug logging based on APP_ENV."""
    return app.config.get('APP_ENV') in ['dev', 'testing']

def should_log_requests(app):
    """Check if we should log requests based on APP_ENV."""
    return app.config.get('APP_ENV') == 'dev'

# Prefer Flask's logger, fallback to print if no app context
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
        return uri  # TODO: NOTES: non-SQLAlchemy URI?

def print_env_info(app: Flask = None):
    """ Print current env & config info for debugging """
    # Check if we should debug log
    if app and not should_debug_log(app):
        return
    
    # Prevent repeated logging on every reload
    if app and getattr(app, "_config_logged", False):
        return
    
    log_info("="*10 + " ENVIRONMENT DEBUG INFO " + "="*15)

    if app:
        config_env = app.config.get('APP_ENV', 'Not set')
        env_var = os.environ.get('APP_ENV', 'Not set (default: dev)')
        log_info(f"Config: {config_env} | APP_ENV: {env_var}")

        # Core flags & DB
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        is_debug = app.config.get('DEBUG', False)
        is_testing = app.config.get('TESTING', False)
        log_info(f"DEBUG: {is_debug} | TESTING: {is_testing}")
        log_info(f"Database URI: {safe_db_uri(db_uri)}")

        app._config_logged = True # don't repeat on reload

    log_info("="*40)

def debug_config(config_name: str, config_class):
    """ Print which config is being loaded """
    log_info(f"\n[CONFIG] Loading {config_name} config: {config_class.__name__}")


def setup_request_debugging(app: Flask = None):
    # Only set up request debugging if in dev config
    if not should_log_requests(app):
        return
    @app.before_request
    def debug_everything():
        # Skip logging for CSS/JS files
        if request.endpoint == 'static':
            return
        
        prefix = "[request_debug]"
        log_info(f"{prefix} {request.method} {request.path} ({request.endpoint})")
        # Only log form data & args if they're not empty
        if request.form:
            log_info(f"{prefix} Form data: {dict(request.form)}")
        if request.args:
            log_info(f"{prefix} Args: {dict(request.args)}")