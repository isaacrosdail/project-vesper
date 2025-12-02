
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.service import TimeTrackingService
from app.modules.time_tracking.viewmodels import (TimeEntryPresenter,
                                                  TimeEntryViewModel)
from app.shared.datetime.helpers import now_in_timezone, last_n_days_range
from app.shared.collections import sort_by_field
from app.shared.decorators import login_plus_session


time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')


@time_tracking_bp.route('/dashboard', methods=["GET"])
@login_plus_session
def dashboard(session: 'Session') -> Any:

    range_days = request.args.get('range', 7, type=int)

    time_entries_sort = request.args.get("time_entries_sort", "started_at")
    time_entries_order = request.args.get("time_entries_order", "desc")

    repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = last_n_days_range(range_days, current_user.timezone)
    time_entries = repo.get_all_time_entries_in_window(start_utc, end_utc)
    time_entries = sort_by_field(time_entries, time_entries_sort, time_entries_order)
    current_date = now_in_timezone(current_user.timezone).date().isoformat()

    viewmodels = [TimeEntryViewModel(e, current_user.timezone) for e in time_entries]
    ctx = {
        "entries": viewmodels,
        "selected_range": range_days,
        "entry_headers": TimeEntryPresenter.build_columns(),
        "current_date": current_date,
        "time_entries_sort": time_entries_sort,
        "time_entries_order": time_entries_order,
    }
    return render_template("time_tracking/dashboard.html", **ctx)


