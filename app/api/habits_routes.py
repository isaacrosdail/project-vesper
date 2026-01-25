from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import date

from flask import Response, request
from flask_login import current_user

import app.shared.datetime.helpers as dth
from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.habits.service import create_habits_service
from app.modules.habits.validators import validate_habit, validate_leetcode_record
from app.shared.decorators import login_plus_session
from app.shared.parsers_ import HABIT_SCHEMA, LEETCODE_SCHEMA, parse_form


@api_bp.post("/habits/habits")
@api_bp.put("/habits/habits/<int:habit_id>")
@login_plus_session
def habits(session: Session, habit_id: int | None = None) -> tuple[Response, int]:
    parsed_data = parse_form(request.form.to_dict(), HABIT_SCHEMA)
    typed_data, errors = validate_habit(parsed_data)

    if errors:
        return validation_failed(errors), 400

    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )

    result = habits_service.save_habit(typed_data, habit_id)
    if not result["success"]:
        return api_response(
            success=False, message=result["message"], errors=result["errors"]
        ), 400

    habit = result["data"]["habit"]
    status_code = 201 if request.method == "POST" else 200

    return api_response(
        success=True, message=result["message"], data=habit.to_api_dict()
    ), status_code


@api_bp.route("/habits/<int:habit_id>/completions", methods=["POST", "DELETE"])
@login_plus_session
def completions(session: Session, habit_id: int) -> tuple[Response, int]:
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )

    habit = habits_service.habit_repo.get_by_id(habit_id)
    if not habit:
        return api_response(success=False, message="Habit not found"), 404

    if request.method == "POST":
        completed_at = dth.parse_js_instant(request.get_json()["completed_at"])
        completion = habits_service.completion_repo.create_habit_completion(
            habit_id, completed_at
        )

        habits_service.session.flush()
        progress = habits_service.calculate_all_habits_percentage_this_week()
        return api_response(
            success=True,
            message="Habit marked complete",
            data=completion.to_api_dict() | {"progress": progress},
        ), 201

    if request.method == "DELETE":
        date_received = request.args.get("date", "today")
        if date_received == "today":
            start_utc, end_utc = dth.today_range_utc(current_user.timezone)
        else:
            parsed_date = date.fromisoformat(date_received)
            start_utc, end_utc = dth.day_range_utc(parsed_date, current_user.timezone)

        habit_completion = (
            habits_service.completion_repo.get_habit_completion_in_window(
                habit_id, start_utc, end_utc
            )
        )

        if habit_completion:
            habits_service.completion_repo.delete(habit_completion)
            progress = habits_service.calculate_all_habits_percentage_this_week()
            return api_response(
                success=True,
                message="Habit unmarked as complete",
                data={"progress": progress},
            ), 200
        return api_response(success=False, message="No completion found"), 404
    msg = f"Unexpected method: {request.method}"
    raise AssertionError(msg)


@api_bp.get("/habits/completions/summary")
@login_plus_session
def horizontal_barchart(session: Session) -> tuple[Response, int]:
    last_n_days = int(request.args["lastNDays"])

    start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    aggregate_data = (
        habits_service.completion_repo.get_completion_counts_by_habit_in_window(
            start_utc, end_utc
        )
    )

    chart_data = [{"name": name, "count": count} for name, count in aggregate_data]

    return api_response(
        success=True,
        message=f"Retrieved completion counts for {len(chart_data)} habits",
        data=chart_data,
    ), 200


@api_bp.post("/habits/leetcode_records")
@login_plus_session
def leetcode_records(session: Session) -> tuple[Response, int]:
    parsed_data = parse_form(request.form.to_dict(), LEETCODE_SCHEMA)
    typed_data, errors = validate_leetcode_record(parsed_data)
    if errors:
        return validation_failed(errors), 400

    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )

    record = habits_service.leetcode_repo.create_leetcoderecord(
        leetcode_id=typed_data["leetcode_id"],
        title=typed_data.get("title"),
        difficulty=typed_data["difficulty"],
        language=typed_data["language"],
        status=typed_data["status"],
    )

    return api_response(
        success=True, message="LeetCode record added", data=record.to_api_dict()
    ), 201
