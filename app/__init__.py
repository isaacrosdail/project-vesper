import os
import secrets
# For environment variables via dotenv
from dotenv import load_dotenv
from flask import Flask, g

from alembic import command
# For pivoting to using Alembic instead of create_all
from alembic.config import Config as AlembicConfig
from app.core.api import api_bp
from app.core.auth.routes import auth_bp
from app.config import config_map
from app.core.crud_routes import crud_bp
from app.core.database import db_session, init_db

from app.common.debug import request_debugging

from flask_login import LoginManager

# Import Blueprints
from app.core.routes import main_bp
from app.modules.groceries.routes import groceries_bp
from app.modules.habits.routes import habits_bp
from app.modules.metrics.routes import metrics_bp
from app.modules.tasks.routes import tasks_bp
from app.modules.time_tracking.routes import time_tracking_bp
from app._internal.health_routes import internal_bp

from app.core.constants import DEFAULT_LANG

# Central app factory => Loads configs, inits extensions, runs DB migrations, registers blueprints, & sets global helpers, too
# Using our APP_ENV over Flask's built-ins
def create_app(config_name=None):
    app = Flask(__name__)

    # Determine which config to load, if not passed => read the APP_ENV var, default to dev
    config_name = config_name or os.environ.get('APP_ENV', 'dev')

    if config_name not in config_map:
        raise RuntimeError(f"Unknown APP_ENV '{config_name}'")
    
    # Takes config class (DevConfig, ProdConfig, etc) from config_map & copy all class attrs into app.config
    app.config.from_object(config_map[config_name])

    # Makes sure app.config has an "APP_ENV" key
    # If config class already has APP_ENV defined, does nothing?
    # If it doesn't, it sets it to the value from the class    
    app.config.setdefault("APP_ENV", config_map[config_name].APP_ENV)

    # Debug what's being loaded
    from .common.debug import debug_config, print_env_info
    debug_config(config_name, config_map[config_name])

    # Print full env info (dev or testing)
    if config_name in ('dev', 'testing'):
        print_env_info(app)
        request_debugging(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" # <- where @login_required redirects

    # Flask-Login needs this callback
    # Note: this runs outside the normal request flow? Called whenever Flask-Login needs to reload the user object, even between requests.
    @login_manager.user_loader
    def load_user(user_id):
        from app.core.auth.models import User
        return db_session.get(User, int(user_id))

    # TODO: We need to sort out Plotly's nonsense (injects inline styles/JS) or scrap nonces & strict CSP
    # Generate nonce once per-request (allows our inline theme JS to execute)
    @app.before_request
    def generate_nonce():
        g.nonce = secrets.token_urlsafe(16)

    # Context processor runs before every template render
    # Make is_dev available in all templates globally
    # So we can do {% if is_dev %} to hide dev-only stuff _without_ needing to keep passing it into each template
    @app.context_processor
    def inject_globals():
        return dict(
            is_dev=(app.config['APP_ENV'] == 'dev'), # Prefer config over raw os.environ now that we pick config class from env
            default_lang=DEFAULT_LANG,
            nonce=getattr(g, 'nonce', '') # inject our nonce here as well
        )
    
    # Apply CSP headers
    @app.after_request
    def apply_csp(response):
        response.headers['Content-Security-Policy'] = (
            f"default-src 'self'; "
            # unsafe-inline defeats much of the point of CSP, but Plotly won't play nice
            f"script-src 'self' 'unsafe-inline' https://cdn.plot.ly; " # Should be => f"script-src 'self' 'nonce-{g.nonce}'; "
            f"style-src 'self' 'unsafe-inline'; " # unsafe-inline since Plotly injects inline styles :/
            f"img-src 'self' data:;"
            f"object-src 'none'; "
            f"base-uri 'self';"
        )
        return response

    # Initialize DB
    # TODO: Move auto-migration here into CI instead, disable on prod
    with app.app_context():
        init_db(app.config)
        if app.config["AUTO_MIGRATE"]:
            # Run Alembic migration(s) on startup (in leiu of old 'create_all' method)
            alembic_cfg = AlembicConfig("alembic.ini")     # "Hey Alembic, here's your config file"
            alembic_cfg.set_main_option("sqlalchemy.url", app.config["SQLALCHEMY_DATABASE_URI"]) # Make Alembic use the same db URL our Flask app is using instead of whatever APP_ENV/alembic.ini/'alembic/env.py' might try to guess.
            command.upgrade(alembic_cfg, "head")           # "Run alembic upgrade head but from inside Python"

    # Remove session after each request or app context teardown
    @app.teardown_appcontext
    def remove_session(exception=None):
        db_session.remove()

    _register_blueprints(app)

    return app


def _register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(crud_bp)
    app.register_blueprint(groceries_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(time_tracking_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(internal_bp)