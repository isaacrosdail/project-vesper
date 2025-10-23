
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.service import TimeTrackingService
from app.modules.time_tracking.viewmodels import (TimeEntryPresenter,
                                                  TimeEntryViewModel)
from app.shared.datetime.helpers import today_range_utc, now_in_timezone
from app.shared.sorting import bubble_sort

time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')


@time_tracking_bp.route('/dashboard', methods=["GET"])
@login_required
@with_db_session
def dashboard(session):
    repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = today_range_utc(current_user.timezone)
    #entries = repo.get_all_time_entries_in_window(start_utc, end_utc)
    entries = repo.get_all_time_entries()
    bubble_sort(entries, 'started_at', reverse=True)
    current_date = now_in_timezone(current_user.timezone).date().isoformat()

    viewmodels = [TimeEntryViewModel(e, current_user.timezone) for e in entries]
    ctx = {
        "entries": viewmodels,
        "entry_headers": TimeEntryPresenter.build_columns(),
        "current_date": current_date,
    }
    return render_template("time_tracking/dashboard.html", **ctx)


