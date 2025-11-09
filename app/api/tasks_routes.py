
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import request
from flask_login import current_user

from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.tasks.repository import TasksRepository
from app.modules.tasks.service import TasksService
from app.modules.tasks.validators import validate_task
from app.shared.parsers import parse_task_form_data
from app.shared.decorators import login_plus_session


@api_bp.route("/tasks/tasks", methods=["POST"])
@api_bp.route("/tasks/tasks/<int:task_id>", methods=["PUT"])
@login_plus_session
def tasks(session: 'Session', task_id: int | None = None) -> Any:
    """Create or update a task (POST for new, PUT for edit)."""
    parsed_data = parse_task_form_data(request.form.to_dict())
    typed_data, errors = validate_task(parsed_data)
    if errors:
        return validation_failed(errors), 400

    tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
    tasks_service = TasksService(tasks_repo, current_user.timezone)

    result = tasks_service.save_task(typed_data, task_id) # None -> POST, else -> PUT

    if not result["success"]:
        return api_response(False, result["message"], errors=result["errors"])
    
    tasks_repo.session.flush()
    progress = tasks_service.calculate_tasks_progress_today()
    print(f"Dict response: {progress}", file=sys.stderr)
    task = result["data"]["task"]
    return api_response(
        True,
        result["message"],
        data = task.to_api_dict() | {"progress": progress}
    ), 201