
from datetime import date

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.habits.repository import HabitsRepository
from app.shared.datetime.helpers import (day_range, parse_js_instant,
                                         today_range)
from app.shared.sorting import bubble_sort
from app.modules.habits.viewmodels import HabitPresenter, HabitViewModel
from app.modules.habits.models import Difficulty, Language, LCStatus

habits_bp = Blueprint('habits', __name__, template_folder="templates", url_prefix="/habits")


@habits_bp.route("/dashboard", methods=["GET"])
@login_required
@with_db_session
def dashboard(session):
    
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habits = habits_repo.get_all_habits_and_tags()

    viewmodels = [HabitViewModel(h, current_user.timezone) for h in habits]
    ctx = {
        "headers": HabitPresenter.build_columns(),
        "habits": viewmodels
    }
    return render_template("habits/dashboard.html", **ctx)

@habits_bp.route("/", methods=["GET", "POST"])
@login_required
@with_db_session
def habits(session):
    # Process form data from modal
    if request.method == "POST":
        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        new_habit = habits_repo.create_habit(request.form.get("name"))
        return jsonify({
            "success": True, 
            "message": "Habit added",
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
        if not body:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400
        
        completed_at = parse_js_instant(body["completed_at"])
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"success": False, "message": "Invalid request data"}), 400
    
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habit = habits_repo.get_habit_by_id(habit_id)

    if not habit:
        return jsonify({"success": False, "message": "Habit not found"}), 404
    
    habit_completion = habits_repo.create_habit_completion(habit_id, completed_at)
    return jsonify({"success": True, "message": "Habit marked complete"}), 201


# Note: JS-side is flexible enough to delete any given date's completion
@habits_bp.route("/<int:habit_id>/completion", methods=["DELETE"])
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
    

@habits_bp.route("/leetcode_record", methods=["POST"])
@login_required
@with_db_session
def create_leetcoderecord(session):
    form_data = request.form.to_dict()

    try:
        form_data["difficulty"] = Difficulty(form_data["difficulty"])
        form_data["language"] = Language(form_data["language"])
        form_data["lcstatus"] = LCStatus(form_data["lcstatus"])
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
    form_data["leetcode_id"] = int(form_data["leetcode_id"])

    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    new_record = habits_repo.create_leetcoderecord(**form_data)

    return jsonify({
        "success": True,
        "message": "LeetCode record added",
        "new_record": {
            "id": new_record.id,
            "leetcode_id": new_record.leetcode_id,
            "title": new_record.title,
            "difficulty": new_record.difficulty.value,
            "language": new_record.language.value,
            "lcstatus": new_record.status.value
        }
    })