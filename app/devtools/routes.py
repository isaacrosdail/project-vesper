"""Development tools blueprint.

Provides:
- /style-reference  : Internal UI style guide (dev only, owner access)
"""
import os
import sys
from flask import request
from flask import Blueprint, current_app, render_template
from flask_login import login_required

from app.modules.auth.service import owner_required

devtools_bp = Blueprint("devtools", __name__, url_prefix="/devtools", template_folder="templates")


if os.environ.get("APP_ENV") == "dev":
    @devtools_bp.get("/style_reference")
    @login_required # type: ignore
    def style_reference() -> tuple[str, int]:
        """NOTE: Only registered in `dev` environment."""
        return render_template("style-reference.html"), 200

@devtools_bp.get("/routes")
@owner_required
def show_routes() -> tuple[str, int]:
    routes = []
    for rule in current_app.url_map.iter_rules():
        methods_set = rule.methods or set()
        methods = ",".join(sorted(methods_set - {"HEAD", "OPTIONS"}))
        routes.append({
            "methods": methods,
            "endpoint": rule.rule,
            "function": rule.endpoint
        })

    return render_template("routes.html", routes=routes), 200
