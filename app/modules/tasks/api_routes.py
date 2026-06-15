from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Response, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import api_response
from app.modules.tasks.schemas import Task, TaskPatch
from app.modules.tasks.service import create_tasks_service
from app.shared.decorators import login_plus_session
from app.shared.exceptions import ServiceError


@api_bp.post("/tasks/tasks")
@login_plus_session
def create_task(session: Session) -> tuple[Response, int]:
    validated = Task(**request.json)

    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)

    task = tasks_service.create_task(validated)
    session.commit()
    progress = tasks_service.calculate_tasks_progress_today()

    return api_response(success=True, message="Task created",
        data=task.to_api_dict() | {"progress": progress}
    ), 201

@api_bp.patch("/tasks/tasks/<int:task_id>")
@login_plus_session
def patch_task(session: Session, task_id: int) -> tuple[Response, int]:
    validated = TaskPatch(**request.json)

    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)
    task = tasks_service.update_task(task_id, validated)
    session.commit()
    progress = tasks_service.calculate_tasks_progress_today()

    return api_response(success=True, message="Task updated",
        data=task.to_api_dict() | {"progress": progress}
    ), 200


@api_bp.get("/tasks/tasks")
@login_plus_session
def tasks_list(session: Session) -> tuple[Response, int]:
    include_links = request.args.get("include_links", "false") == "true"
    last_n_days = request.args.get("lastNDays", type=int)
    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )

    if include_links:
        tasks = tasks_service.task_repo.get_all_tasks_with_links()
    elif last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        tasks = tasks_service.task_repo.get_all_in_window(start_utc, end_utc, date_col="due_date")
    else:
        tasks = tasks_service.task_repo.get_all()

    return api_response(
        success=True,
        message=f"Retrieved {len(tasks)} tasks",
        data = [ t.to_api_dict() for t in tasks ]
    ), 200


@api_bp.get("/tasks/tasks/<int:task_id>")
@login_plus_session
def get_task(session: Session, task_id: int) -> tuple[Response, int]:
    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)
    task = tasks_service.get_task(task_id)
    return api_response(success=True, message="Task retrieved", data=task.to_api_dict()), 200


@api_bp.delete("/tasks/tasks/<int:task_id>")
@login_plus_session
def delete_task(session: Session, task_id: int) -> tuple[Response, int]:
    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)
    tasks_service.delete_task(task_id)
    return api_response(success=True, message="Task deleted"), 200


@api_bp.route("/tasks/task_links", methods = ["POST", "DELETE"])
@login_plus_session
def task_links(session: Session) -> tuple[Response, int]:
    data = request.json
    try:
        sub_id = int(data.get("subtask_id"))
        super_id = int(data.get("supertask_id"))
    except (TypeError, ValueError):
        return api_response(success=False, message="IDs must be integers"), 400

    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )

    if request.method == "POST":
        tasks_service.save_link(sub_id, super_id)
        return api_response(
            success=True,
            message="Link created",
            data={ "subtask_id": sub_id, "supertask_id": super_id }
        ), 201

    tasks_service.delete_link(sub_id, super_id)
    return api_response(success=True, message="Link deleted"), 200

