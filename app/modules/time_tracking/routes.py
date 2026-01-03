
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.modules.time_tracking.service import create_time_tracking_service
from app.modules.time_tracking.viewmodels import (TimeEntryPresenter,
                                                  TimeEntryViewModel)
from app.shared.datetime.helpers import now_in_timezone, last_n_days_range
from app.shared.collections import sort_by_field
from app.shared.decorators import login_plus_session
from app.shared.parsers import get_table_params


time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')


@time_tracking_bp.get('/dashboard')
@login_plus_session
def dashboard(session: 'Session') -> Any:

    time_entries_params = get_table_params('time_entries', 'started_at')

    time_service = create_time_tracking_service(session, current_user.id, current_user.timezone)

    start_utc, end_utc = last_n_days_range(time_entries_params['range'], current_user.timezone)
    time_entries = time_service.time_entry_repo.get_all_time_entries_in_window(start_utc, end_utc)
    time_entries = sort_by_field(time_entries, time_entries_params['sort_by'], time_entries_params['order'])
    viewmodels = [TimeEntryViewModel(e, current_user.timezone) for e in time_entries]

    current_date = now_in_timezone(current_user.timezone).date().isoformat()

    ctx = {
        "time_entries_params": time_entries_params,
        "entry_headers": TimeEntryPresenter.build_columns(),
        "entries": viewmodels,
        "current_date": current_date,
    }
    return render_template("time_tracking/dashboard.html", **ctx)


