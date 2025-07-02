
from flask import Blueprint, request, jsonify, render_template
import sys
from app.modules.time_tracking.models import TimeEntry

from app.core.database import database_connection

from app.utils.visualization.charts import (create_metric_chart_html,
                                            get_metric_dataframe)

time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')

@time_tracking_bp.route('/dashboard', methods=["GET"])
def dashboard():
    
    DEFAULT_DAYS = 14
    with database_connection() as session:
        df = get_metric_dataframe(TimeEntry, "time entries", 7, session)
        time_entries_graph = create_metric_chart_html(df, "time entries")

    return render_template("time_tracking/dashboard.html",
                           time_entries_graph=time_entries_graph)

@time_tracking_bp.route('/', methods=["GET", "POST"])
def time_entries():
    
    try:
        if request.method == 'POST':
        
            # Get JSON data from request => put in dict entry_data
            entry_data =  request.get_json()
            print(entry_data, file=sys.stderr)

            with database_connection() as session:

                # New TimeEntry with that data
                new_time_entry = TimeEntry(
                    category = entry_data.get('category'),
                    duration = float(entry_data.get('duration')),
                    description = entry_data.get('description'),
                )

                # Save to db
                session.add(new_time_entry)

                return jsonify({"success": True, "message": "Time entry added."}), 201

    
        # GET => ? Should we have a bespoke "add_entry" form as well?
        else:
            return jsonify({"message": "GET arriving soon"}), 200
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
