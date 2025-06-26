
from flask import Blueprint, request, jsonify

from app.modules.time_tracking.models import TimeEntry

from app.core.database import database_connection

time_tracking_bp = Blueprint('time_tracking', __name__, template_folder='templates', url_prefix='/time_tracking')

@time_tracking_bp.route('/dashboard', methods=["GET"])
def dashboard():
    # TODO: Add time tracking dashboard template
    pass

@time_tracking_bp.route('/', methods=["GET", "POST"])
def time_entries():
    
    try:
        if request.method == 'POST':
        
            # Get JSON data from request => put in dict entry_data
            entry_data =  request.get_json()

            with database_connection() as session:

                # New TimeEntry with that data
                    new_time_entry = TimeEntry(
                        category = entry_data.get('category'),
                        duration = entry_data.get('duration'),
                        description = entry_data.get('description'),
                    )

                    # Save to db
                    session.add(new_time_entry)
                    session.commit()

                    return jsonify({"success": True, "message": "Time entry added."}), 201

    
        # GET => ? Should we have a bespoke "add_entry" form as well?
        else:
            pass
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
