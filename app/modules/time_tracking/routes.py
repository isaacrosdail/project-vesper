
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.api.responses import api_response, validation_failed
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.service import TimeTrackingService
from app.shared.datetime.helpers import today_range_utc
from app.modules.time_tracking.viewmodels import TimeEntryViewModel, TimeEntryPresenter
from app.modules.time_tracking.validators import validate_time_entry
from app.shared.parsers import parse_time_entry_form_data

time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')

@time_tracking_bp.route('/dashboard', methods=["GET"])
@login_required
@with_db_session
def dashboard(session):
    repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = today_range_utc(current_user.timezone)
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

        parsed_data = parse_time_entry_form_data(request.form.to_dict())

        typed_data, errors = validate_time_entry(parsed_data)
        if errors:
            return validation_failed(errors), 400

        repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
        service = TimeTrackingService(repo, current_user.timezone)
        result = service.create_entry_from_form(typed_data)

        if not result["success"]:
            return api_response(False, result["message"], errors=result["errors"])

        entry = result["data"]["entry"]
        return api_response(
            True,
            result["message"],
            data = {
                "id": entry.id,
                "category": entry.category,
                "duration": entry.duration_minutes,
                "started_at": entry.started_at.isoformat(),
                "description": entry.description
            }
        ), 201
