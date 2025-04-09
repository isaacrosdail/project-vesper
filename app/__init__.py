from flask import Flask
from app.blueprints.grocery_routes import grocery_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(grocery_bp)

    return app