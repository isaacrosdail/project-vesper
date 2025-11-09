
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

from app.modules.metrics.repository import DailyMetricsRepository, ABTestRepository
from app.modules.metrics.service import DailyMetricsService
from app.modules.metrics.viewmodels import (DailyMetricPresenter,
                                            DailyMetricViewModel)
from app.shared.datetime.helpers import now_in_timezone
from app.shared.decorators import login_plus_session


metrics_bp = Blueprint('metrics', __name__, template_folder='templates', url_prefix='/metrics')


@metrics_bp.route('/dashboard', methods=["GET"])
@login_plus_session
def dashboard(session: 'Session') -> Any:

    daily_metrics_repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
    metric_entries = daily_metrics_repo.get_all()

    abtest_repo = ABTestRepository(session, current_user.id, current_user.timezone)
    ab_tests = abtest_repo.get_all()

    today = now_in_timezone(current_user.timezone).date()
    current_date = today.isoformat()

    viewmodels = [DailyMetricViewModel(e, current_user.timezone) for e in metric_entries]
    ctx = {
        "metrics": viewmodels,
        "metric_headers": DailyMetricPresenter.build_columns(),
        "current_date": current_date,
        "ab_tests": ab_tests
    }
    return render_template("metrics/dashboard.html", **ctx)
