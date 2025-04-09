from flask import Flask
from app.database import Base, engine

from app.modules.groceries import models as grocery_models
from app.modules.tasks import models as tasks_models

from app.blueprints.main_routes import main_bp
from app.blueprints.grocery_routes import grocery_bp
from app.blueprints.tasks_routes import tasks_bp

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(grocery_bp)
    app.register_blueprint(tasks_bp)

    # Create tables on app start (for dev only, wrap in environment check later based on config)
    Base.metadata.create_all(engine)

    return app