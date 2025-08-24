import os
import secrets

from flask import Flask, g
from flask_caching import Cache
from flask_login import LoginManager, current_user

from alembic import command
from alembic.config import Config as AlembicConfig
from app._infra.database import db_session, init_db
from app.config import config_map
from app.core.routes import main_bp
from app.devtools.routes import devtools_bp
from app.errors import errors_bp
from app.extensions import _setup_extensions
from app.modules.api.crud_routes import crud_bp
from app.modules.api.routes import api_bp
from app.modules.auth.models import UserRole
from app.modules.auth.routes import auth_bp
from app.modules.groceries.routes import groceries_bp
from app.modules.habits.routes import habits_bp
from app.modules.metrics.routes import metrics_bp
from app.modules.tasks.routes import tasks_bp
from app.modules.time_tracking.routes import time_tracking_bp
from app.shared.constants import DEFAULT_LANG
from app.shared.debug import setup_request_debugging

## TODO: Consider Flask-Compress

def has_dev_tools() -> bool:
    # Before login: current_user.is_authenticated is False, re-evals upon login?
    return bool(
        getattr(current_user, "is_authenticated", False)
        and getattr(current_user, "is_owner", False)
    )

# Global cache instance? Docs unclear
cache = Cache()

# Central app factory => Loads configs, inits extensions, runs DB migrations, registers blueprints, & sets global helpers, too
# Using our APP_ENV over Flask's built-ins
def create_app(config_name: str = None):
    # Determine which config to load, if not passed => read the APP_ENV var, default to dev
    config_name = config_name or os.environ.get('APP_ENV', 'dev')

    if config_name not in config_map:
        raise RuntimeError(f"Unknown APP_ENV '{config_name}'")

    # Serve built files from static on prod, unminified on dev
    # TODO: FIX DEVEE BELOW
    static_dir = "static_src" if os.environ.get("APP_ENV") == "devee" else "static"
    app = Flask(__name__, static_folder=static_dir, template_folder='_templates')

    _apply_config(app, config_name)
    _setup_debug(app, config_name)
    _setup_extensions(app)
    _setup_request_hooks(app)
    _setup_database(app)
    _register_blueprints(app)

    return app


def _setup_database(app) -> None:
    # Initialize DB
    # TODO: Move auto-migration here into CI instead, disable on prod
    with app.app_context():
        init_db(app.config)
        if app.config["AUTO_MIGRATE"]:
            # Run Alembic migration(s) on startup
            alembic_cfg = AlembicConfig("alembic.ini")     # "Hey Alembic, here's your config file"
            alembic_cfg.set_main_option("sqlalchemy.url", app.config["SQLALCHEMY_DATABASE_URI"]) # Make Alembic use the same db URL our Flask app is using instead of whatever APP_ENV/alembic.ini/'alembic/env.py' might try to guess.
            command.upgrade(alembic_cfg, "head")           # "Run alembic upgrade head but from inside Python"

    # Hook db_session.remove() into teardown
    # Prevents sessions leaking between requests
    @app.teardown_appcontext
    def remove_session(exception=None):
        db_session.remove()


def _register_blueprints(app) -> None:
    blueprints = [
        main_bp, auth_bp, crud_bp, groceries_bp, tasks_bp, habits_bp, 
        api_bp, metrics_bp, time_tracking_bp, devtools_bp, errors_bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)


def _apply_config(app, config_name) -> None:
    # Takes config class (DevConfig, ProdConfig, etc) from config_map & copy all class attrs into app.config
    app.config.from_object(config_map[config_name])

    # Makes sure app.config has an "APP_ENV" key
    # If config class already has APP_ENV defined, does nothing?
    # If it doesn't, it sets it to the value from the class    
    app.config.setdefault("APP_ENV", config_map[config_name].APP_ENV)


def _setup_debug(app, config_name) -> None:
    # Debug what's being loaded
    from .shared.debug import debug_config, print_env_info
    debug_config(config_name, config_map[config_name])

    # Print full env info (dev or testing)
    if config_name in ('dev', 'testing'):
        print_env_info(app)
        setup_request_debugging(app)


def _setup_request_hooks(app):
    # Before each request: Evaluate has_dev_tools, generate nonce (allows our inline theme JS to execute)
    @app.before_request
    def generate_nonce():
        g.nonce = secrets.token_urlsafe(16)
        g.has_dev_tools = has_dev_tools()

    # Context processor runs before every template render
    # Injects helpful globals (can reference globally as regular vars)
    @app.context_processor
    def inject_globals():
        return dict(
            has_dev_tools=has_dev_tools, # Prefer config over raw os.environ now that we pick config class from env
            default_lang=DEFAULT_LANG,
            nonce=getattr(g, 'nonce', ''), # inject our nonce here as well,
            UserRole=UserRole   # Make our UserRole Enum available for role checks in templates directly
        )
    
    # Apply CSP headers
    @app.after_request
    def apply_csp(response):
        response.headers['Content-Security-Policy'] = (
            f"default-src 'self'; "
            f"script-src 'self' https://vesper.isaacrosdail.com; "
            f"style-src 'self' https://vesper.isaacrosdail.com; "
            f"img-src 'self' data:;"
            f"object-src 'none'; "
            f"base-uri 'self';"
        )
        return response