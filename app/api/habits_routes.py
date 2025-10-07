
from datetime import date

from flask import request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import HabitsService
from app.modules.habits.validators import (validate_habit,
                                           validate_leetcode_record)
from app.shared.datetime.helpers import (day_range_utc, parse_js_instant,
                                         today_range_utc)
from app.shared.parsers import parse_habit_form_data, parse_leetcode_form_data


@api_bp.route("/habits/habits", methods=["GET", "POST"])
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
    


@api_bp.route("/habits/<int:habit_id>/completions", methods=["POST", "DELETE"])
@login_required
@with_db_session
def completions(session, habit_id):
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habit = habits_repo.get_habit_by_id(habit_id)
    
    if not habit:
        return api_response(False, "Habit not found"), 404

    if request.method == "POST":
        completed_at = parse_js_instant(request.get_json()["completed_at"])
        habit_completion = habits_repo.create_habit_completion(habit_id, completed_at)
        return api_response(
            True, 
            "Habit marked complete",
            data={"completion_id": habit_completion.id}
        ), 201

    elif request.method == "DELETE":
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



@api_bp.route("/habits/leetcode_records", methods=["POST"])
@login_required
@with_db_session
def leetcode_records(session):
    parsed_data = parse_leetcode_form_data(request.form.to_dict())
    typed_data, errors = validate_leetcode_record(parsed_data)
    if errors:
        return validation_failed(errors), 400

    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)

    record = habits_repo.create_leetcoderecord(
        leetcode_id=typed_data["leetcode_id"],
        title=typed_data.get("title"),
        difficulty=typed_data["difficulty"],
        language=typed_data["language"],
        status=typed_data["status"],
    )

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