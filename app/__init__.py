from flask import Flask
from app.core.config import config_map
#from app.core.config import DevConfig, TestConfig
from app.core.database import init_db


# Import DB stuff
from app.modules.groceries import models as grocery_models
from app.modules.tasks import models as tasks_models

# Import Blueprints
from app.core.routes import main_bp
from app.modules.groceries.routes import groceries_bp
from app.modules.tasks.routes import tasks_bp

def create_app(config_name="dev"): # Default to DevConfig if nothing is passed in
    app = Flask(__name__)

    # Load appropriate config based on environment
    app.config.from_object(config_map[config_name])

    #with app.app_context():
    #    init_db(app.config)

    app.register_blueprint(main_bp)
    app.register_blueprint(groceries_bp)
    app.register_blueprint(tasks_bp)

    return app