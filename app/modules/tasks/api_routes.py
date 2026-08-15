from __future__ import annotations

from typing import TYPE_CHECKING

from app.modules.tasks.models import Task

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Response, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import success_response
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskLink,
    TaskPatch,
    TaskProgressRead,
    TaskRead,
    TaskStatRead,
)
from app.modules.tasks.service import create_tasks_service
from app.shared.decorators import login_plus_session


@api_bp.post("/tasks/tasks")
@login_plus_session
def create_task(session: Session) -> tuple[Response, int]:
    validated = TaskCreate(**request.json)

    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)

    task = tasks_service.create_task(validated)
    session.commit()
    progress = tasks_service.calculate_tasks_progress_today()

    return success_response(message="Task created",
        data=TaskRead.dump(task)
            | { "progress": TaskProgressRead.dump(progress) }
    ), 201

@api_bp.patch("/tasks/tasks/<int:task_id>")
@login_plus_session
def patch_task(session: Session, task_id: int) -> tuple[Response, int]:
    validated = TaskPatch(**request.json)

    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)
    task = tasks_service.update_task(task_id, validated)
    session.commit()
    progress = tasks_service.calculate_tasks_progress_today()

    return success_response(message="Task updated",
        data=TaskRead.dump(task)
            | { "progress": TaskProgressRead.dump(progress) }
    ), 200


@api_bp.get("/tasks/tasks")
@login_plus_session
def tasks_list(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )

    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        tasks = tasks_service.task_repo.get_all_in_window(start_utc, end_utc, date_col=Task.due_datetime)
    else:
        tasks = tasks_service.task_repo.get_all()

    return success_response(
        message=f"Retrieved {len(tasks)} tasks",
        data = [ TaskRead.dump(t) for t in tasks ]
    ), 200


@api_bp.get("/tasks/tasks/<int:task_id>")
@login_plus_session
def get_task(session: Session, task_id: int) -> tuple[Response, int]:
    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)
    task = tasks_service.get_task(task_id)
    return success_response(message="Task retrieved", data=TaskRead.dump(task)), 200


@api_bp.delete("/tasks/tasks/<int:task_id>")
@login_plus_session
def delete_task(session: Session, task_id: int) -> tuple[Response, int]:
    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)
    tasks_service.delete_task(task_id)
    return success_response(message="Task deleted"), 200


@api_bp.post("/tasks/task_links")
@login_plus_session
def create_task_link(session: Session) -> tuple[Response, int]:
    link = TaskLink.model_validate(request.json or {})
    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )
    tasks_service.save_link(link.subtask_id, link.supertask_id)
    return success_response(message="Link created",
        data={ "subtask_id": link.subtask_id, "supertask_id": link.supertask_id }), 201


@api_bp.delete("/tasks/task_links")
@login_plus_session
def delete_task_link(session: Session) -> tuple[Response, int]:
    link = TaskLink.model_validate(request.json or {})
    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )
    tasks_service.delete_link(link.subtask_id, link.supertask_id)
    return success_response(message="Link deleted"), 200


@api_bp.get("/tasks/stats")
@login_plus_session
def get_tasks_stats(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )
    overdue_stat = tasks_service.calc_overdue_rate(days=last_n_days)
    frog_stat = tasks_service.calc_frog_adherence_rate(days=last_n_days)

    return success_response(message="", data={
        "overdue": TaskStatRead.dump(overdue_stat),
        "frog": TaskStatRead.dump(frog_stat)
    }), 200
