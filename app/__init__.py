import os

# For environment variables via dotenv
from dotenv import load_dotenv
from flask import Flask

# For pivoting to using Alembic instead of create_all
from alembic.config import Config as AlembicConfig
from alembic import command

from app.core.database import db_session, init_db
# Import Blueprints
from app.core.routes import main_bp
from app.modules.crud_routes import crud_bp
from app.modules.groceries.routes import groceries_bp
from app.modules.habits.routes import habits_bp
from app.modules.tasks.routes import tasks_bp
from app.core.api import api_bp
from app.modules.metrics.routes import metrics_bp
from app.core.config import DevConfig, ProdConfig, TestConfig, config_map


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('APP_ENV', 'dev')

    app = Flask(__name__)

    # Debug what's being loaded
    from .utils.debug import debug_config, print_env_info
    debug_config(config_name, config_map[config_name])

    # Load appropriate config based on environment
    app.config.from_object(config_map[config_name])

    # Print full env info (dev/testing)
    if config_name == 'dev' or 'testing':
        print_env_info(app)

    # Context processor runs before every template render
    # Make is_dev available in all templates globally
    # So we can do {% if is_dev %} to hide dev-only stuff _without_ needing to keep passing it into each template
    @app.context_processor
    def inject_dev_context():
        return dict(is_dev=os.environ.get('APP_ENV') == 'dev')

    # Initialize DB (and optionally seed it with seed_db - Will pivot from this though when adding auth)
    with app.app_context():
        init_db(app.config)

        # Instead of create_all, now let Alembic handle it by running migrations
        alembic_cfg = AlembicConfig("alembic.ini")     # "Hey Alembic, here's your config file"
        command.upgrade(alembic_cfg, "head")           # "Run alembic upgrade head but from inside Python"

        # Run seed_db for prod to fill with dummy data
        if config_name == 'prod':
            from .seed_db import seed_db
            seed_db()

    # Remove session after each request or app context teardown
    @app.teardown_appcontext
    def remove_session(exception=None):
        db_session.remove()

    app.register_blueprint(main_bp)
    app.register_blueprint(crud_bp)
    app.register_blueprint(groceries_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(metrics_bp)

    return app