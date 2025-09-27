
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.api.responses import api_response, validation_failed
from app.modules.metrics.service import DailyMetricsService
from app.modules.metrics.repository import DailyMetricsRepository
from app.modules.metrics.viewmodels import DailyMetricViewModel, DailyMetricPresenter
from app.shared.datetime.helpers import today_range_utc
from app.modules.metrics.validators import validate_daily_entry

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
    
    form_data = request.form.to_dict()
    errors = validate_daily_entry(form_data)
    if errors:
        return validation_failed(errors), 400
    
    repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
    service = DailyMetricsService(repo, current_user.timezone)

    result = service.process_daily_metrics(form_data)


    return api_response(
        True,
        result["message"],
        data = result["data"] # pass through the data dict
    ), 201
