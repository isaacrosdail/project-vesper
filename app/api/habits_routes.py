
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import date

from flask import request
from flask_login import current_user

from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import HabitsService
from app.modules.habits.validators import (validate_habit,
                                           validate_leetcode_record)
from app.shared.datetime.helpers import (day_range_utc, last_n_days_range,
                                         parse_js_instant, today_range_utc)
from app.shared.decorators import login_plus_session
from app.shared.parsers import parse_habit_form_data, parse_leetcode_form_data


@api_bp.route("/habits/habits", methods=["POST"])
@api_bp.route("/habits/habits/<int:habit_id>", methods=["PUT"])
@login_plus_session
def habits(session: 'Session', habit_id: int | None = None) -> Any:
        parsed_data = parse_habit_form_data(request.form.to_dict())
        typed_data, errors = validate_habit(parsed_data)

        if errors:
            return validation_failed(errors), 400

        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        habits_service = HabitsService(habits_repo, current_user.timezone)
        result = habits_service.save_habit(typed_data, habit_id)

        if not result["success"]:
            return api_response(False, result["message"], errors=result["errors"])
        

        habit = result["data"]["habit"]
        return api_response(
            True,
            result["message"],
            data = habit.to_api_dict()
        ), 201
    


@api_bp.route("/habits/<int:habit_id>/completions", methods=["POST", "DELETE"])
@login_plus_session
def completions(session: 'Session', habit_id: int) -> Any:
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habits_service = HabitsService(habits_repo, current_user.timezone)
    habit = habits_repo.get_by_id(habit_id)
    
    if not habit:
        return api_response(False, "Habit not found"), 404

    if request.method == "POST":
        completed_at = parse_js_instant(request.get_json()["completed_at"])
        completion = habits_repo.create_habit_completion(habit_id, completed_at)
        habits_repo.session.flush()
        progress = habits_service.calculate_all_habits_percentage_this_week()
        return api_response(
            True, 
            "Habit marked complete",
            data= completion.to_api_dict() | {"progress": progress} # | merge operator to tack onto dict
        ), 201

    elif request.method == "DELETE":
        date_received = request.args.get('date', 'today')
        if date_received == 'today':
            start_utc, end_utc = today_range_utc(current_user.timezone)
        else:
            parsed_date = date.fromisoformat(date_received) # NOTE: add method to notes
            start_utc, end_utc = day_range_utc(parsed_date, current_user.timezone)

        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        habit_completion = habits_repo.get_habit_completion_in_window(habit_id, start_utc, end_utc)
        
        if habit_completion:
            habits_repo.delete(habit_completion)
            progress = habits_service.calculate_all_habits_percentage_this_week()
            return api_response(True, "Habit unmarked as complete", data={"progress": progress}), 200
        else:
            return api_response(False, "No completion found"), 404

@api_bp.get("/habits/completions/summary")
@login_plus_session
def horizontal_barchart(session: 'Session') -> Any:
    last_n_days = int(request.args["lastNDays"])
    repo = HabitsRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = last_n_days_range(last_n_days, current_user.timezone)
    aggregate_data = repo.get_completion_counts_by_habit_in_window(start_utc, end_utc)

    chart_data = [
        {"name": name, "count": count}
        for name, count in aggregate_data
    ]

    return api_response(
        True,
        f"Retrieved completion counts for {len(chart_data)} habits",
        data=chart_data
    ), 200

@api_bp.route("/habits/leetcode_records", methods=["POST"])
@login_plus_session
def leetcode_records(session: 'Session') -> Any:
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
        data = record.to_api_dict()
    ), 201