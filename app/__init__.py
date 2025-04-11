from flask import Flask
from .config import DevConfig, TestConfig
#from .database import get_db_session, Base
from app.base import Base
from .config import config_map

# Import DB stuff
from app.modules.groceries import models as grocery_models
from app.modules.tasks import models as tasks_models

# Import Blueprints
from app.blueprints.main_routes import main_bp
from app.blueprints.grocery_routes import grocery_bp
from app.blueprints.tasks_routes import tasks_bp

def create_app(config_name="dev"): # Default to DevConfig if nothing is passed in
    app = Flask(__name__)

    # Load appropriate config based on environment
    app.config.from_object(config_map[config_name])

    app.register_blueprint(main_bp)
    app.register_blueprint(grocery_bp)
    app.register_blueprint(tasks_bp)

    return app