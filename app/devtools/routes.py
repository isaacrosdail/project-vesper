"""Development tools blueprint.

Provides:
- /style-reference  : Internal UI style guide (dev only, owner access)
"""

import os

from flask import Blueprint, render_template

from app.shared.decorators import typed_login_required

devtools_bp = Blueprint(
    "devtools", __name__, url_prefix="/devtools", template_folder="templates"
)


if os.environ.get("APP_ENV") == "dev":
    @devtools_bp.get("/style_reference")
    @typed_login_required
    def style_reference() -> tuple[str, int]:
        """NOTE: Only registered in `dev` environment."""
        return render_template("style-reference.html"), 200

