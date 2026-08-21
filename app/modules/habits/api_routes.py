from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import TypeAdapter

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import date, datetime

from flask import Response, abort, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import success_response
from app.modules.habits.schemas import (
    HabitCompletionCreate,
    HabitCompletionProgressRead,
    HabitCompletionRead,
    HabitCreate,
    HabitDayRead,
    HabitOverviewItemRead,
    HabitPatch,
    HabitRead,
)
from app.modules.habits.service import create_habits_service
from app.shared.decorators import login_plus_session


@api_bp.post("/habits/habits")
@login_plus_session
def habits(session: Session) -> tuple[Response, int]:
    ## TODO(habits): vet/check
    HABIT_CREATE_ADAPTER: TypeAdapter[HabitCreate] = TypeAdapter(HabitCreate)
    validated = HABIT_CREATE_ADAPTER.validate_python(request.json)
    # validated = HabitCreate(**request.json)
    habits_service = create_habits_service(session, current_user.id, current_user.timezone)
    habit = habits_service.create_habit(validated)
    return success_response(message="Habit created", data=HabitRead.dump(habit)), 201


@api_bp.patch("/habits/habits/<int:habit_id>")
@login_plus_session
def patch_habit(session: Session, habit_id: int) -> tuple[Response, int]:
    validated = HabitPatch(**request.json)
    habit_svc = create_habits_service(session, current_user.id, current_user.timezone)
    habit = habit_svc.update_habit(validated, habit_id)
    return success_response(message="Habit updated", data=HabitRead.dump(habit)), 200


@api_bp.get("/habits/habits")
@login_plus_session
def habits_list(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    habits_service = create_habits_service(session, current_user.id, current_user.timezone)

    # TODO(repo): last n days doesnt even make sense for habits?
    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        results = habits_service.habit_repo.get_all_in_window(start_utc, end_utc)
    else:
        results = habits_service.habit_repo.get_all()
    data = [HabitRead.dump(h) for h in results]

    return success_response(message=f"Retrieved {len(results)} habits", data=data), 200


@api_bp.get("/habits/habits/<int:habit_id>")
@login_plus_session
def get_habit(session: Session, habit_id: int) -> tuple[Response, int]:
    habits_service = create_habits_service(session, current_user.id, current_user.timezone)
    habit = habits_service.get_habit(habit_id)
    return success_response(message="Habit retrieved", data=HabitRead.dump(habit)), 200


@api_bp.delete("/habits/habits/<int:habit_id>")
@login_plus_session
def delete_habit(session: Session, habit_id: int) -> tuple[Response, int]:
    habits_service = create_habits_service(session, current_user.id, current_user.timezone)
    habits_service.delete_habit(habit_id)
    return success_response(message="Habit deleted"), 200


@api_bp.post("/habits/<int:habit_id>/completions")
@login_plus_session
def add_completion(session: Session, habit_id: int) -> tuple[Response, int]:
    validated = HabitCompletionCreate(**request.json)
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )

    completion, progress = habits_service.save_completion(habit_id, validated)
    return success_response(
        message="Habit marked complete",
        data = HabitCompletionRead.dump(completion)
            | { "progress": HabitCompletionProgressRead.dump(progress) }
    ), 201


@api_bp.delete("/habits/<int:habit_id>/completions")
@login_plus_session
def delete_completion(session: Session, habit_id: int) -> tuple[Response, int]:
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    date_str = request.args.get("date", "today")

    progress = habits_service.delete_completion(habit_id, date_str)
    return success_response(
        message="Habit unmarked as complete",
        data={ "progress": HabitCompletionProgressRead.dump(progress) },
    ), 200


@api_bp.get("/habits/habit_completions/summary")
@login_plus_session
def horizontal_barchart(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    if last_n_days is None:
        abort(400, description="Query parameter 'lastNDays' is required and must be an integer.")

    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    aggregate_data = habits_service.completions_summary(last_n_days)

    return success_response(
        message=f"Retrieved completion counts for {len(aggregate_data)} habits",
        data=aggregate_data,
    ), 200

@api_bp.get("/habits/habit_completions/heatmap")
@login_plus_session
def completions_heatmap(session: Session) -> tuple[Response, int]:
    habit_id = request.args.get("habit_id", type=int)
    # Full-year 12mos. for this year TODO: frotend needs to match - is that a design flaw?
    now_utc = dth.now_utc()
    start_utc = datetime(now_utc.year, 1, 1, tzinfo=now_utc.tzinfo)
    end_utc = datetime(now_utc.year + 1, 1, 1, tzinfo=now_utc.tzinfo)

    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    heatmap_data = habits_service.completion_repo.get_completion_counts_in_window(start_utc, end_utc, habit_id)

    return success_response(
        message=f"Retrieved {len(heatmap_data)} entries for heatmap",
        data=heatmap_data
    ), 200



@api_bp.get("/habits/overview")
@login_plus_session
def get_habits_overview(session: Session) -> tuple[Response, int]:
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    habits = habits_service.habit_repo.get_all()

    streaks = habits_service.get_all_streaks()
    start_utc, end_utc = dth.today_range_utc(current_user.timezone)
    todays_completions = habits_service.completion_repo.get_all_in_window(start_utc, end_utc)
    completed_today_ids = {c.habit_id for c in todays_completions if c.satisfied}
    consistencies = habits_service.calc_consistency_all()

    week = habits_service.get_week_completions_by_habit()
    week_intended = habits_service.week_intended_by_habit()
    items = [HabitOverviewItemRead(**HabitRead.dump(h),
                completed_today=h.id in completed_today_ids,
                streak_count=streaks.get(h.id, 0),
                consistency=consistencies.get(h.id),
                week_intended=week_intended.get(h.id),
                data=[HabitDayRead.model_validate(c) for c in week.get(h.id, [])])
                for h in habits
            ]
    progress = habits_service.calculate_all_habits_percentage_this_week()
    return success_response(
        message="Retrieved overview",
        data={
            "habits": [HabitOverviewItemRead.dump(i) for i in items],
            "progress": HabitCompletionProgressRead.dump(progress)
        }
    ), 200
