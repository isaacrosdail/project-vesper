"""
Development tools blueprint.

Provides:
- /style-reference  : Internal UI style guide (dev only, owner access)
"""
import os

from flask import Blueprint, render_template
from flask_login import login_required

devtools_bp = Blueprint('devtools', __name__, url_prefix='/devtools', template_folder='templates')


# Only register style_reference in development
if os.environ.get('APP_ENV') == 'dev':
    @devtools_bp.route('/style_reference')
    @login_required
    def style_reference():
        return render_template('style-reference.html')