import os

# For environment variables via dotenv
from dotenv import load_dotenv
from flask import Flask

from app.core.config import config_map
from app.core.database import db_session, init_db
# Import Blueprints
from app.core.routes import main_bp
from app.modules.crud_routes import crud_bp
from app.modules.groceries.routes import groceries_bp
from app.modules.tasks.routes import tasks_bp


def create_app(config_name=None):

    # Load environment variables
    load_dotenv()

    app = Flask(__name__)

    # If no config provided, check Flask_ENV for environment
    if config_name is None:
        # Get FLASK_ENV and default to 'dev' if not set
        env = os.environ.get('FLASK_ENV', 'development')
        config_name = 'prod' if env == 'production' else 'dev'

    print(f"Using config: {config_name}")

    # Load appropriate config based on environment
    app.config.from_object(config_map[config_name])

    # Initialize DB (and optionally seed it with seed_db - Will pivot from this though when adding auth)
    with app.app_context():
        init_db(app.config)
        # Run seed_db for prod to fill with dummy data
        if app.config['ENV'] == 'production':
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

    return app