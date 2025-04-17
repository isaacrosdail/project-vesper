from flask import Flask
from app.core.config import config_map
from app.core.database import init_db, db_session

# Import DB stuff
from app.modules.groceries import models as grocery_models
from app.modules.tasks import models as tasks_models

# Import Blueprints
from app.core.routes import main_bp
from app.modules.groceries.groceries_routes import groceries_bp
from app.modules.tasks.routes import tasks_bp
from app.modules.crud_routes import crud_bp

def create_app(config_name="dev"): # Default to DevConfig if nothing is passed in
    app = Flask(__name__)

    # Load appropriate config based on environment
    app.config.from_object(config_map[config_name])

    with app.app_context():
        init_db(app.config)

    # Remove session after each request or app context teardown
    @app.teardown_appcontext
    def remove_session(exception=None):
        db_session.remove()

    app.register_blueprint(main_bp)
    app.register_blueprint(crud_bp)
    app.register_blueprint(groceries_bp)
    app.register_blueprint(tasks_bp)

    return app