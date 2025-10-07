from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from app.api import (
    routes,
    generic_routes,
    groceries_routes,
    habits_routes,
    tasks_routes,
    metrics_routes,
    time_tracking_routes,
)