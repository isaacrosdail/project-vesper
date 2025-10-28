
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.metrics.repository import DailyMetricsRepository
from app.modules.metrics.service import DailyMetricsService
from app.modules.metrics.viewmodels import (DailyMetricPresenter,
                                            DailyMetricViewModel)
from app.shared.datetime.helpers import now_in_timezone


metrics_bp = Blueprint('metrics', __name__, template_folder='templates', url_prefix='/metrics')


@metrics_bp.route('/dashboard', methods=["GET"])
@login_required
@with_db_session
def dashboard(session):

    repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
    metric_entries = repo.get_all_daily_metrics()

    today = now_in_timezone(current_user.timezone).date()
    current_date = today.isoformat()

    viewmodels = [DailyMetricViewModel(e, current_user.timezone) for e in metric_entries]
    ctx = {
        "metrics": viewmodels,
        "metric_headers": DailyMetricPresenter.build_columns(),
        "current_date": current_date
    }
    return render_template("metrics/dashboard.html", **ctx)
