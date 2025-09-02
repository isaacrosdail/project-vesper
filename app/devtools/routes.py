"""
Development tools blueprint.

Provides:
- /health   : JSON health check endpoint (for monitoring)
- /style-reference  : Internal UI style guide (dev only, owner access)
"""
import os

from flask import Blueprint, jsonify, render_template
from flask_login import login_required

from app.shared.constants import DEFAULT_HEALTH_TIMEZONE
from app.shared.datetime.helpers import convert_to_timezone

devtools_bp = Blueprint('devtools', __name__, url_prefix='/devtools', template_folder='templates')

@devtools_bp.route('/health')
def health_check():
    """Basic health check for monitoring."""
    status = {
        'status': 'healthy',
        'timestamp': convert_to_timezone(DEFAULT_HEALTH_TIMEZONE)
    }
    return jsonify(status)

# Only register style_reference in development
if os.environ.get('APP_ENV') == 'dev':
    @devtools_bp.route('/style_reference')
    @login_required
    def style_reference():
        return render_template('style-reference.html')