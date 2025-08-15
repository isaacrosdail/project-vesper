
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import database_connection
from app.modules.metrics.repository import DailyMetricsRepository
from app.shared.datetime.helpers import today_range
from app.shared.sorting import bubble_sort

metrics_bp = Blueprint('metrics', __name__, template_folder='templates', url_prefix='/metrics')


@metrics_bp.route('/dashboard', methods=["GET"])
@login_required
def dashboard():

    with database_connection() as session:

        # Instantiate repository class
        repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
        entries = repo.get_all_daily_metrics()

        ### Add new viz here

        # Get list of all metrics for table, sort by date for now
        bubble_sort(entries, 'created_at', reverse=True)

        ctx = {
            "metrics": entries,
        }
        return render_template("metrics/dashboard.html", **ctx)


@metrics_bp.route("/", methods=["POST"])
@login_required
def metrics():
    data = request.get_json()
    try:
        with database_connection() as session:
            # Instantiate our repository
            repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)

            # TODO: Validators.py
            metric_type=data["metric_type"]
            value=data["value"]

            start_utc, end_utc = today_range(current_user.timezone)
            new_metric = repo.create_or_update_daily_metric(metric_type, value, start_utc, end_utc)

            return jsonify({"success": True, "message": "Successfully added metric"}), 201

    # TODO: Security - don't expose internal errors to users, need to adjust
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500