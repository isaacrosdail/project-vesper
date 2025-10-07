from flask import request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.tasks.repository import TasksRepository
from app.modules.tasks.service import TasksService
from app.modules.tasks.validators import validate_task
from app.shared.parsers import parse_task_form_data


@api_bp.route("/tasks/tasks", methods=["POST"])
@api_bp.route("/tasks/tasks/<int:task_id>", methods=["PATCH"])
@login_required
@with_db_session
def tasks(session, task_id=None):
    """Create or update a task (POST for new, PATCH for edit)."""
    parsed_data = parse_task_form_data(request.form.to_dict())
    typed_data, errors = validate_task(parsed_data)
    if errors:
        return validation_failed(errors), 400

    tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
    tasks_service = TasksService(tasks_repo, current_user.timezone)

    result = tasks_service.save_task(typed_data, task_id) # None -> POST, else -> PATCH

    if not result["success"]:
        return api_response(False, result["message"], errors=result["errors"])
    
    task = result["data"]["task"]
    return api_response(
        True,
        result["message"],
        data = {
            "id": task.id,
            "name": task.name,
            "is_done": task.is_done,
            "priority": task.priority.value,
            "is_frog": task.is_frog,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "subtype": "tasks"
        }
    ), 201