
from datetime import date

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.api.responses import api_response, validation_failed
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import HabitsService
from app.modules.habits.validators import (validate_habit,
                                           validate_leetcode_record)
from app.modules.habits.viewmodels import HabitPresenter, HabitViewModel
from app.shared.datetime.helpers import (day_range_utc, parse_js_instant,
                                         today_range_utc)
from app.shared.parsers import parse_habit_form_data, parse_leetcode_form_data


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

        parsed_data = parse_habit_form_data(request.form.to_dict())
        typed_data, errors = validate_habit(parsed_data)

        if errors:
            return validation_failed(errors), 400

        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        habits_service = HabitsService(habits_repo, current_user.timezone)
        result = habits_service.create_habit(typed_data)

        if not result["success"]:
            return api_response(False, result["message"], errors=result["errors"])
        

        habit = result["data"]["habit"]
        return api_response(
            True,
            result["message"],
            data = {
                "id": habit.id,
                "name": habit.name
            }
        ), 201
    

@habits_bp.route("/<int:habit_id>/completions", methods=["POST"])
@login_required
@with_db_session
def completions(session, habit_id):

    completed_at = parse_js_instant(request.get_json()["completed_at"])
    
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


# TODO: Tidy. Note: JS-side is flexible enough to delete any given date's completion
@habits_bp.route("/<int:habit_id>/completion", methods=["DELETE"])
@login_required
@with_db_session
def completion(session, habit_id):

    date_received = request.args.get('date', 'today')

    if date_received == 'today':
        start_utc, end_utc = today_range_utc(current_user.timezone)
    else:
        parsed_date = date.fromisoformat(date_received)
        start_utc, end_utc = day_range_utc(parsed_date, current_user.timezone)

    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habit_completion = habits_repo.get_habit_completion_in_window(habit_id, start_utc, end_utc)
    
    if habit_completion:
        habits_repo.delete(habit_completion)
        return api_response(True, "Habit unmarked as complete"), 200
    else:
        return api_response(False, "No completion found"), 404
    

@habits_bp.route("/leetcode_record", methods=["POST"])
@login_required
@with_db_session
def create_leetcoderecord(session):

    parsed_data = parse_leetcode_form_data(request.form.to_dict())
    typed_data, errors = validate_leetcode_record(parsed_data)

    if errors:
        return validation_failed(errors), 400

    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    record = habits_repo.create_leetcoderecord(**typed_data)

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