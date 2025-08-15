
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import database_connection
from app.modules.time_tracking.models import TimeEntry
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.shared.constants import DEFAULT_CHART_DAYS
from app.shared.datetime.helpers import last_n_days_range

time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')

@time_tracking_bp.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    
    with database_connection() as session:
        repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
        start_utc, end_utc = last_n_days_range(DEFAULT_CHART_DAYS, current_user.timezone)
        entries = repo.get_entries_by_category_in_window("Programming", start_utc, end_utc)

        return render_template("time_tracking/dashboard.html")

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
