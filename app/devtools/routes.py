"""
Development tools blueprint.

Provides:
- /style-reference  : Internal UI style guide (dev only, owner access)
"""
import os

from flask import Blueprint, render_template, abort, current_app
from flask_login import login_required, current_user

from app.modules.auth.service import requires_owner


devtools_bp = Blueprint('devtools', __name__, url_prefix='/devtools', template_folder='templates')


# Only register style_reference in development
if os.environ.get('APP_ENV') == 'dev':
    @devtools_bp.route('/style_reference')
    @login_required
    def style_reference():
        return render_template('style-reference.html')
    
@devtools_bp.route('/routes')
@requires_owner
def show_routes():
    if not current_user.is_owner:
        abort (403)

    routes = []
    for rule in current_app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        routes.append({
            'methods': methods,
            'endpoint': rule.rule,
            'function': rule.endpoint
        })

    return render_template('routes.html', routes=routes)