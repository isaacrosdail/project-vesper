from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from app.api import (
    routes,
    generic_routes,
)

from app.modules.groceries import api_routes as groceries_api
from app.modules.habits import api_routes as habits_api
from app.modules.metrics import api_routes as metrics_api
from app.modules.tasks import api_routes as tasks_api
from app.modules.time_tracking import api_routes as time_tracking_api
