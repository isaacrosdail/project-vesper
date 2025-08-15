
from datetime import date

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.habits.repository import HabitsRepository
from app.shared.datetime.helpers import (day_range, parse_js_instant,
                                         today_range)
from app.shared.sorting import bubble_sort

habits_bp = Blueprint('habits', __name__, template_folder="templates", url_prefix="/habits")


@habits_bp.route("/dashboard", methods=["GET"])
@login_required
@with_db_session
def dashboard(session):
    
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habits = habits_repo.get_all_habits_and_tags()
    bubble_sort(habits, 'created_at', reverse=True)

    # TODO: build_columns() => Make a helper, not internal method
    headers = ["Name", "Status", "Created"]
    ctx = {
        "headers": headers,
        "habits": habits
    }
    return render_template("habits/dashboard.html", **ctx)

# CREATE
@habits_bp.route("/", methods=["GET", "POST"])
@login_required
@with_db_session
def habits(session):
    # Process form data from modal
    if request.method == "POST":
        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        new_habit = habits_repo.create_habit(request.form.get("name"))
        flash("Habit added successfully.")
        return jsonify({
            "success": True, 
            "message": "Habit added successfully.",
            "habit": {
                "id": new_habit.id,
                "name": new_habit.name,
            }
        })
    
# Creates a new HabitCompletion record to mark a Habit complete & enable more robust habit analytics in future
@habits_bp.route("/<int:habit_id>/completions", methods=["POST"])
@login_required
@with_db_session
def completions(session, habit_id):
    try:
        body = request.get_json() # returns dict, parse JSON body of POST fetch
        completed_at = parse_js_instant(body["completed_at"])

        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        habit = habits_repo.get_habit_by_id(habit_id)

        if not habit:
            return jsonify({"success": False, "message": "Habit not found"}), 404
        
        habit_completion = habits_repo.create_habit_completion(habit_id)
        return jsonify({"success": True, "message": "Habit marked complete"}), 201
        
    except Exception:
        return jsonify({"success": False, "message": "Failed to mark habit complete"}), 500
    

# Deletes a given HabitCompletion record (acts as our "habit marked complete")
# For now, we'll only allow habits to have a single completion record in a given day
# BUT this is now flexible enough to allow for choosing the day whose completion we wish to delete
@habits_bp.route("/<int:habit_id>/completions", methods=["DELETE"])
@login_required
@with_db_session
def completion(session, habit_id):

    date_received = request.args.get('date', 'today') # default to today

    if date_received == 'today':
        start_utc, end_utc = today_range(current_user.timezone)
    else:
        # Parse date, convert to range
        parsed_date = date.fromisoformat(date_received)
        start_utc, end_utc = day_range(parsed_date, current_user.timezone)

    # Find corresponding habitcompletion entry for today
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habit_completion = habits_repo.get_habit_completion_in_window(habit_id, start_utc, end_utc)
    
    if habit_completion:
        session.delete(habit_completion)
        return jsonify({"success": True, "message": "Habit unmarked as complete"}), 200
    else:
        return jsonify({"success": False, "message": "No completion found for today"}), 404

    # except Exception:
    #     return jsonify({"success": False, "message": "Failed to unmark habit"}), 500 # 500 = Internal Server Error