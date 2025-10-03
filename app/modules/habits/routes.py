
from datetime import date

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.api.responses import api_response, validation_failed
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import HabitsService
from app.shared.datetime.helpers import (parse_js_instant,
                                         today_range_utc, day_range_utc)
from app.modules.habits.viewmodels import HabitPresenter, HabitViewModel
from app.modules.habits.models import DifficultyEnum, LanguageEnum, LCStatusEnum, StatusEnum
from app.modules.habits.constants import PROMOTION_THRESHOLD_DEFAULT
from app.modules.habits.validators import validate_habit, validate_leetcode_record
from app.shared.parsers import parse_leetcode_form_data, parse_habit_form_data

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
    if request.method == "POST":

        form_data = request.form.to_dict()
        habit_data = parse_habit_form_data(form_data)

        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        habits_service = HabitsService(habits_repo, current_user.timezone)

        result = habits_service.create_habit(habit_data)
        if not result["success"]:
            return validation_failed(result["errors"]), 400
        

        habit = result["data"]["habit"]
        return api_response(
            True,
            "Habit added", # TODO: Just use result["data"]["message"] here? so services dictate toasts?
            data = {
                "id": habit.id,
                "name": habit.name
            }
        ), 201
    
# Creates a new HabitCompletion record to mark a Habit complete & enable more robust habit analytics in future
@habits_bp.route("/<int:habit_id>/completions", methods=["POST"])
@login_required
@with_db_session
def completions(session, habit_id):
    try:
        body = request.get_json()
        if not body:
            return api_response(False, "Invalid JSON"), 400
        
        completed_at = parse_js_instant(body["completed_at"])
    except (KeyError, ValueError, TypeError) as e:
        return api_response(False, "Invalid request data"), 400
    
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habit = habits_repo.get_habit_by_id(habit_id)

    if not habit:
        return api_response(False, "Habit not found"), 404
    
    habit_completion = habits_repo.create_habit_completion(habit_id, completed_at)
    return api_response(
        True, 
        "Habit marked complete",
        data={"completion_id": habit_completion.id}
    ), 201


# Note: JS-side is flexible enough to delete any given date's completion
@habits_bp.route("/<int:habit_id>/completion", methods=["DELETE"])
@login_required
@with_db_session
def completion(session, habit_id):

    date_received = request.args.get('date', 'today') # default to today

    if date_received == 'today':
        start_utc, end_utc = today_range_utc(current_user.timezone)
    else:
        # Parse date, convert to range
        parsed_date = date.fromisoformat(date_received)
        start_utc, end_utc = day_range_utc(parsed_date, current_user.timezone)

    # Find corresponding habitcompletion entry for today
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habit_completion = habits_repo.get_habit_completion_in_window(habit_id, start_utc, end_utc)
    
    if habit_completion:
        session.delete(habit_completion)
        return api_response(True, "Habit unmarked as complete"), 200
    else:
        return api_response(False, "No completion found for today"), 404
    

@habits_bp.route("/leetcode_record", methods=["POST"])
@login_required
@with_db_session
def create_leetcoderecord(session):

    leetcode_data = parse_leetcode_form_data(request.form.to_dict())

    errors = validate_leetcode_record(leetcode_data)
    if errors:
        return api_response(False, errors), 400

    # Convert to proper types
    try:
        processed_data = {
            "leetcode_id": int(leetcode_data["leetcode_id"]),
            "title": leetcode_data["title"],
            "difficulty": DifficultyEnum(leetcode_data["difficulty"]),
            "language": LanguageEnum(leetcode_data["language"]),
            "lcstatus": LCStatusEnum(leetcode_data["status"])
        }
    except (ValueError, KeyError):
        return api_response(False, "Invalid data format"), 400

    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    record = habits_repo.create_leetcoderecord(**processed_data)

    return api_response(
        True,
        "LeetCode record added",
        data = {
            "id": record.id,
            "leetcode_id": record.leetcode_id,
            "title": record.title,
            "difficulty": record.difficulty.value,
            "language": record.language.value,
            "lcstatus": record.status.value
        }
    ), 201