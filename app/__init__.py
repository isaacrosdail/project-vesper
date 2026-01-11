import logging
import secrets
from typing import Any

from alembic.config import Config as AlembicConfig
from flask import Flask, current_app, g, Response
from flask_caching import Cache
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

from alembic import command
from app._infra.database import db_session, init_db
from app.config import get_config
from app.extensions import _setup_extensions
from app.modules.auth.models import UserRoleEnum
from app.shared import jinja_filters
from app.shared.debug import setup_dev_debugging
from app.shared.setup_logging import setup_logging

def has_dev_tools() -> bool:
    """Dev tools visible to anyone in dev, owner-only in prod."""
    if current_app.config["APP_ENV"] == "dev":
        return True

    return bool(
        current_user.is_authenticated
        and current_user.is_owner
    )

# Global cache instance? Docs unclear
cache = Cache()


def create_app(config_name: str | None = None) -> Flask:
    """Central app factory. Loads configs, extensions, register blueprints, etc."""

    app = Flask(__name__, template_folder="_templates")

    _apply_config(app, config_name)
    setup_logging(app)              # Must read logging level after being set by apply_config
    if config_name in ("dev", "testing"):
        setup_dev_debugging(app)
    _setup_extensions(app)
    _setup_request_hooks(app)
    _setup_database(app)
    _register_blueprints(app)

    jinja_filters.register_filters(app)

    return app


def _setup_database(app: Flask) -> None:
    """
    Initialize database engine, session, and optionally run migrations.

    Sets up SQLAlchemy engine and configures the database session. If AUTO_MIGRATE is enabled,
    runs Alembic migrations programmatically (equivalent to `alembic upgrade head`)
    Inits database with `app.app_context()`. If app.config's `AUTO_MIGRATE` flag is set to true, then runs
    Alembic migration(s) as well, using `SQLALCHEMY_DATABASE_URI`'s value as `sqlalchemy.url`.
    
    Note: When running migrations using command.upgrade(), we need to explicitly set `sqlalchemy.url` because
    programmatic calls don't use `alembic/env.py` (unlike CLI commands).

    Registers a teardown handler to clean up database sessions after each request.
    """
    with app.app_context():
        init_db(app.config)
        if app.config["AUTO_MIGRATE"]:
            alembic_cfg = AlembicConfig("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", app.config["SQLALCHEMY_DATABASE_URI"])
            command.upgrade(alembic_cfg, "head")

        # Set logging level back after Alembic borks it
        logging.getLogger().setLevel(app.config["LOGGING_LEVEL"])

    # Hook db_session.remove() into teardown
    # Prevents sessions leaking between requests
    @app.teardown_appcontext
    def remove_session(exception=None): # type: ignore
        db_session.remove()


def _register_blueprints(app: Flask) -> None:
    """
    Imports and register all application blueprints.

    Blueprints are imported here (not at module level) for two reasons:
    1. Ensures setup_logging() runs before blueprint imports, so module-level
    logger = logging.getLogger(__name__) declarations work correctly.
    2. Avoids circular import issues when blueprint files import from app.
    """
    # Import blueprints here so setup_logging() runs BEFORE these imports
    # That way we can have logger = logging.getLogger(__name__) declared top-level in files since it resolves after our logger is set up
    from app.api import api_bp
    from app.devtools.routes import devtools_bp
    from app.errors import errors_bp
    from app.modules.auth.routes import auth_bp
    from app.modules.groceries.routes import groceries_bp
    from app.modules.habits.routes import habits_bp
    from app.modules.metrics.routes import metrics_bp
    from app.modules.tasks.routes import tasks_bp
    from app.modules.time_tracking.routes import time_tracking_bp
    from app.routes import main_bp
    blueprints = [
        main_bp, auth_bp, api_bp, groceries_bp, tasks_bp, habits_bp,
        metrics_bp, time_tracking_bp, devtools_bp, errors_bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)


def _apply_config(app: Flask, config_name: str | None) -> None:
    """
    Copies our config from config_name into app config? (same as current_app?)
    Takes config class (DevConfig, ProdConfig, etc) from config_map & copy all class attrs into app.config
    """
    app.config.from_object(get_config(config_name))

    # For Flask to play nice with CSP headers
    if app.config.get("USE_PROXY_FIX", False):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1) # type: ignore


def _setup_request_hooks(app: Flask) -> None:
    """
    Register Flask request lifecycle hooks.

    Namely:
    - before_request: Generates CSP nonce and checks dev tools privileges.
    - context_processor: Injects globals (has_dev_tools, nonce, UserRoleEnum) into all templates
    """
    # Before each request: Evaluate has_dev_tools, generate nonce (allows our inline theme JS to execute)
    @app.before_request
    def generate_nonce() -> None:
        g.nonce = secrets.token_urlsafe(16)
        g.has_dev_tools = has_dev_tools()

    # Context processor runs before every template render
    # Injects helpful globals (can reference globally as regular vars)
    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        return dict(
            has_dev_tools=has_dev_tools, # Prefer config over raw os.environ now that we pick config class from env
            nonce=getattr(g, "nonce", ""), # inject our nonce here as well,
            UserRole=UserRoleEnum   # Make our UserRoleEnum available for role checks in templates directly
        )

    # Apply CSP headers
    @app.after_request
    def apply_csp(response: Response) -> Any:
        import os, sys
        from flask import request
        if request.endpoint == 'devtools.style_reference' or request.endpoint == 'static':
            return response

        # if os.environ.get('APP_ENV') == 'dev':
        #     # Much simpler dev CSP - no nonces, no HTTPS
        #     response.headers['Content-Security-Policy'] = (
        #         "default-src 'self'; "
        #         "script-src 'self' 'unsafe-inline'; "
        #         "style-src 'self' 'unsafe-inline'; "
        #         "img-src 'self' data:; "
        #         "object-src 'none'; "
        #         "base-uri 'self';"
        #     )
        print(request.endpoint, file=sys.stderr)
            # return response
        # Get current domain
        current_host = request.host
        nonce = getattr(g, 'nonce', '')

        response.headers['Content-Security-Policy'] = (
            f"default-src 'self'; "
            f"script-src 'self' https://vesper.isaacrosdail.com 'nonce-{nonce}';"
            f"style-src 'self' https://vesper.isaacrosdail.com 'nonce-{nonce}';"
            f"img-src 'self' data:;"
            f"object-src 'none'; "
            f"base-uri 'self';"
        )
        return response
