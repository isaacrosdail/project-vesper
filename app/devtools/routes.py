"""
Development tools blueprint.

Provides:
- /style-reference  : Internal UI style guide (dev only, owner access)
"""
from typing import Any

import os

from flask import Blueprint, render_template, current_app
from flask_login import login_required

from app.modules.auth.service import requires_owner


devtools_bp = Blueprint('devtools', __name__, url_prefix='/devtools', template_folder='templates')


# Only register style_reference in development
if os.environ.get('APP_ENV') == 'dev':
    @devtools_bp.get('/style_reference')
    @login_required # type: ignore
    def style_reference() -> Any:
        return render_template('style-reference.html')
    
@devtools_bp.get('/routes')
@requires_owner
def show_routes() -> Any:
    routes = []
    for rule in current_app.url_map.iter_rules():
        methods_set = rule.methods or set()
        methods = ','.join(sorted(methods_set - {'HEAD', 'OPTIONS'}))
        routes.append({
            'methods': methods,
            'endpoint': rule.rule,
            'function': rule.endpoint
        })

    return render_template('routes.html', routes=routes)