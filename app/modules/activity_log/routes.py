
from flask import Blueprint




activity_log_bp = Blueprint('activity_log', __name__, template_folder='templates', url_prefix='/activity_log')

@activity_log_bp.route('/', methods=["GET"])
def dashboard():
    pass

@activity_log_bp.route('/', methods=["POST"])
def add():
    pass