
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import database_connection
from app.modules.time_tracking.models import TimeEntry
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.shared.datetime.helpers import today_range
from app.modules.time_tracking.viewmodels import TimeEntryViewModel, TimeEntryPresenter

time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')

@time_tracking_bp.route('/dashboard', methods=["GET"])
@login_required
@with_db_session
def dashboard(session):
    repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = today_range(current_user.timezone)
    time_entries = repo.get_all_time_entries_in_window(start_utc, end_utc)

    viewmodels = [TimeEntryViewModel(e, current_user.timezone) for e in time_entries]
    ctx = {
        "time_entries": viewmodels,
        "time_entry_headers": TimeEntryPresenter.build_columns()
    }
    return render_template("time_tracking/dashboard.html", **ctx)

@time_tracking_bp.route('/', methods=["GET", "POST"])
@login_required
def time_entries():
    try:
        if request.method == 'POST':
            form_data =  request.get_json() # JSON => dict

            with database_connection() as session:
                timetracking_repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
                timetracking_repo.create_time_entry(**form_data)

                return jsonify({"success": True, "message": "Time entry added."}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
