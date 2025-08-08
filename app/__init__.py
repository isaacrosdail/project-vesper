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
from app.core.config import config_map
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

def create_app(config_name=None):
    app = Flask(__name__)

    config_name = config_name or os.environ.get('APP_ENV', 'dev')
    
    # Load appropriate config based on environment
    app.config.from_object(config_map[config_name])
    
    # Debug what's being loaded
    from .common.debug import debug_config, print_env_info
    debug_config(config_name, config_map[config_name])

    # Print full env info (dev/testing)
    if config_name == 'dev' or 'testing':
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
            is_dev=os.environ.get('APP_ENV') == 'dev',
            default_lang=DEFAULT_LANG,
            nonce=getattr(g, 'nonce', '') # inject our nonce here as well
        )
    
    # Add to CSP headers
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

    # Initialize DB (and optionally seed it with seed_db - Will pivot from this though when adding auth)
    with app.app_context():
        init_db(app.config)

        # Instead of create_all, now let Alembic handle it by running migrations
        alembic_cfg = AlembicConfig("alembic.ini")     # "Hey Alembic, here's your config file"
        command.upgrade(alembic_cfg, "head")           # "Run alembic upgrade head but from inside Python"

        # Run seed_db for prod to fill with dummy data
        if config_name == 'prod':
            from .common.database.seed.seed_db import seed_db
            seed_db()

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