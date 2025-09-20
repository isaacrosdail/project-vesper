
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import database_connection, with_db_session
from app.modules.metrics.repository import DailyMetricsRepository
from app.modules.metrics.viewmodels import DailyMetricViewModel, DailyMetricPresenter
from app.shared.datetime.helpers import today_range
from app.shared.sorting import bubble_sort

metrics_bp = Blueprint('metrics', __name__, template_folder='templates', url_prefix='/metrics')


@metrics_bp.route('/dashboard', methods=["GET"])
@login_required
@with_db_session
def dashboard(session):

    # Instantiate repository class
    repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
    metric_entries = repo.get_all_daily_metrics()

    viewmodels = [DailyMetricViewModel(e, current_user.timezone) for e in metric_entries]
    ctx = {
        "metrics": viewmodels,
        "metric_headers": DailyMetricPresenter.build_columns()
    }
    return render_template("metrics/dashboard.html", **ctx)


@metrics_bp.route("/", methods=["POST"])
@login_required
@with_db_session
def metrics(session):
        
    repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)

    data = request.form.to_dict()
    start_utc, end_utc = today_range(current_user.timezone)
    # Iterate over key-value pairs, calling create/update for each whose value is a non-empty string (which is falsy in Python)
    processed_metrics = []
    for metric_type, value in data.items():
        if value:
            metric, was_created = repo.create_or_update_daily_metric(metric_type, value, start_utc, end_utc)
            processed_metrics.append({"metric_type": metric_type, "created": was_created })

    return jsonify({
        "success": True, 
        "message": f"Added {len(processed_metrics)} metrics",
        "metrics": processed_metrics
    }), 201
