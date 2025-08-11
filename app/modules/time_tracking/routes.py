
from flask import Blueprint, jsonify, render_template, request

from app.common.visualization.charts import (create_metric_chart_html,
                                             get_filtered_dataframe)
from app.core.constants import DEFAULT_CHART_DAYS
from app.core.database import database_connection
from app.modules.time_tracking.models import TimeEntry
from flask_login import current_user, login_required

time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')

@time_tracking_bp.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    
    with database_connection() as session:
        df = get_filtered_dataframe(session, TimeEntry, current_user.id, "category", "Programming", "duration", DEFAULT_CHART_DAYS)
        time_entries_graph = create_metric_chart_html(df, "time_entries")

        return render_template("time_tracking/dashboard.html",
                                time_entries_graph=time_entries_graph)

@time_tracking_bp.route('/', methods=["GET", "POST"])
@login_required
def time_entries():
    try:
        if request.method == 'POST':
            # Get JSON data from request => put in dict form_data
            form_data =  request.get_json()

            with database_connection() as session:

                # New TimeEntry with that data
                new_time_entry = TimeEntry(
                    category = form_data.get('category'),
                    duration = float(form_data.get('duration')),
                    description = form_data.get('description'),
                )
                session.add(new_time_entry)

                return jsonify({"success": True, "message": "Time entry added."}), 201

    
        # No GET => Modal-driven
        else:
            return jsonify({"message": "GET arriving soon"}), 200
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
