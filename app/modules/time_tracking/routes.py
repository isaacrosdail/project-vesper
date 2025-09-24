
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.service import TimeTrackingService
from app.shared.datetime.helpers import today_range, parse_datetime_from_hhmm, add_mins_to_datetime
from app.modules.time_tracking.viewmodels import TimeEntryViewModel, TimeEntryPresenter
from app.modules.time_tracking.validators import validate_time_entry

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
@with_db_session
def time_entries(session):
    if request.method == 'POST':
        form_data = request.form.to_dict()

        timetracking_repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
        service = TimeTrackingService(timetracking_repo)

        result = service.create_entry_from_form(form_data, current_user.timezone)

        if not result["success"]:
            return jsonify(result), 400

        entry = result["entry"]
        return jsonify({
            "success": True, 
            "message": "Time entry added",
            "data": {
                "id": entry.id,
                "category": entry.category,
                "duration": entry.duration,
                "started_at": entry.started_at.isoformat(),
                "description": entry.description
            }
        }), 201
