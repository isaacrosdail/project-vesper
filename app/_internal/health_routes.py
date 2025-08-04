# Getting started with HTTP health checks

from flask import Blueprint, jsonify

from app.common.datetime.helpers import now_local
from app.core.constants import DEFAULT_HEALTH_TIMEZONE

internal_bp = Blueprint('_internal', __name__, url_prefix='/_internal')

@internal_bp.route('/health')
def health_check():
    """Basic health check for monitoring."""
    status = {
        'status': 'healthy',
        'timestamp': now_local(DEFAULT_HEALTH_TIMEZONE)
    }
    return jsonify(status)