from flask import Blueprint, render_template

errors_bp = Blueprint("errors", __name__)

# TODO: NOTES:
# These aren't "routes", they're callbacks Flask runs when a request raises a specific HTTP error.
# We trigger them by causing the matching error.
@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return render_template("errors/500.html"), 500