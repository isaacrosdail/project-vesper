from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime

from flask import Response, abort, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import api_response
from app.modules.habits.schemas import Habit, HabitPatch, LCRecord
from app.modules.habits.service import create_habits_service
from app.shared.decorators import login_plus_session
from app.shared.exceptions import ServiceError


@api_bp.post("/habits/habits")
@login_plus_session
def habits(session: Session) -> tuple[Response, int]:
    validated = Habit(**request.json)

    habits_service = create_habits_service(session, current_user.id, current_user.timezone)
    habit = habits_service.create_habit(validated)
    return api_response(success=True, message="Habit created", data=habit.to_api_dict()), 201


@api_bp.patch("/habits/habits/<int:habit_id>")
@login_plus_session
def patch_habit(session: Session, habit_id: int) -> tuple[Response, int]:
    validated = HabitPatch(**request.json)
    habit_svc = create_habits_service(session, current_user.id, current_user.timezone)
    habit = habit_svc.update_habit(validated, habit_id)
    return api_response(success=True, message="Habit updated", data=habit.to_api_dict()), 200


@api_bp.get("/habits/habits")
@login_plus_session
def habits_list(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    habits_service = create_habits_service(session, current_user.id, current_user.timezone)

    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        results = habits_service.habit_repo.get_all_habits_and_tags_in_window(start_utc, end_utc)
    else:
        results = habits_service.habit_repo.get_all()
    data = [t.to_api_dict() for t in results]

    return api_response(success=True, message=f"Retrieved {len(results)} habits", data=data), 200


@api_bp.post("/habits/<int:habit_id>/completions")
@login_plus_session
def add_completion(session: Session, habit_id: int) -> tuple[Response, int]:
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    completed_at = dth.parse_js_instant(request.get_json()["completed_at"])

    completion, progress = habits_service.save_completion(habit_id, completed_at)
    return api_response(
        success=True,
        message="Habit marked complete",
        data=completion.to_api_dict() | {"progress": progress},
    ), 201


@api_bp.delete("/habits/<int:habit_id>/completions")
@login_plus_session
def delete_completion(session: Session, habit_id: int) -> tuple[Response, int]:
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    date_str = request.args.get("date", "today")

    progress = habits_service.delete_completion(habit_id, date_str)
    return api_response(
        success=True,
        message="Habit unmarked as complete",
        data={"progress": progress},
    ), 200


@api_bp.get("/habits/habit_completions/summary")
@login_plus_session
def horizontal_barchart(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    if last_n_days is None:
        abort(400, description="Query parameter 'lastNDays' is required and must be an integer.")

    start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    aggregate_data = (
        habits_service.completion_repo.get_completion_counts_by_habit_in_window(
            start_utc, end_utc
        )
    )

    return api_response(
        success=True,
        message=f"Retrieved completion counts for {len(aggregate_data)} habits",
        data=aggregate_data,
    ), 200

@api_bp.get("/habits/habit_completions/heatmap")
@login_plus_session
def completions_heatmap(session: Session) -> tuple[Response, int]:
    # Full-year 12mos. for this year TODO: frotend needs to match - is that a design flaw?
    now_utc = dth.now_utc()
    start_utc = datetime(now_utc.year, 1, 1, tzinfo=now_utc.tzinfo)
    end_utc = datetime(now_utc.year + 1, 1, 1, tzinfo=now_utc.tzinfo)

    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    heatmap_data = habits_service.completion_repo.get_completion_counts_in_window(start_utc, end_utc)

    return api_response(
        success=True,
        message=f"Retrieved {len(heatmap_data)} entries for heatmap",
        data=heatmap_data
    ), 200


@api_bp.post("/habits/leetcode_records")
@login_plus_session
def leetcode_records(session: Session) -> tuple[Response, int]:
    validated = LCRecord(**request.json)

    habits_service = create_habits_service(session, current_user.id, current_user.timezone)

    record = habits_service.leetcode_repo.create_leetcoderecord(
        leetcode_id=validated.leetcode_id,
        title=validated.title,
        difficulty=validated.difficulty,
        language=validated.language,
        status=validated.status,
    )

    return api_response(
        success=True, message="LeetCode record added", data=record.to_api_dict()
    ), 201


@api_bp.get("/habits/leet_code_records")
@login_plus_session
def leet_code_records_list(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    habits_service = create_habits_service(session, current_user.id, current_user.timezone)

    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        results = habits_service.leetcode_repo.get_all_in_window(start_utc, end_utc)
    else:
        results = habits_service.leetcode_repo.get_all()
    data = [t.to_api_dict() for t in results]

    return api_response(success=True, message=f"Retrieved {len(results)} Leetcode records", data=data), 200
