from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Response, request
from flask_login import current_user

from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.tasks.service import create_tasks_service
from app.modules.tasks.validators import validate_task
from app.shared.decorators import login_plus_session
from app.shared.parsers_ import TASK_SCHEMA, parse_form


@api_bp.post("/tasks/tasks")
@api_bp.put("/tasks/tasks/<int:task_id>")
@login_plus_session
def tasks(session: "Session", task_id: int | None = None) -> tuple[Response, int]:
    """Create or update a task (POST for new, PUT for edit)."""
    parsed_data = parse_form(request.form.to_dict(), TASK_SCHEMA)
    typed_data, errors = validate_task(parsed_data)
    if errors:
        return validation_failed(errors), 400

    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )

    result = tasks_service.save_task(typed_data, task_id)  # None -> POST, else -> PUT

    if not result["success"]:
        return api_response(
            success=False, message=result["message"], errors=result["errors"]
        ), 400

    tasks_service.session.flush()
    progress = tasks_service.calculate_tasks_progress_today()

    task = result["data"]["task"]
    status_code = 201 if request.method == "POST" else 200

    return api_response(
        success=True,
        message=result["message"],
        data=task.to_api_dict() | {"progress": progress},
    ), status_code
