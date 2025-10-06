
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.api.responses import api_response, validation_failed
from app.modules.tasks.models import PriorityEnum
from app.modules.tasks.service import TasksService
from app.modules.tasks.repository import TasksRepository
from app.modules.tasks.viewmodels import TaskViewModel, TaskPresenter
from app.shared.parsers import parse_task_form_data
from app.modules.tasks.validators import validate_task


tasks_bp = Blueprint('tasks', __name__, template_folder="templates", url_prefix="/tasks")

@tasks_bp.route("/dashboard", methods=["GET"])
@login_required
@with_db_session
def dashboard(session):

    tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
    tasks = tasks_repo.get_all_tasks()
    
    viewmodel = [TaskViewModel(t, current_user.timezone) for t in tasks]

    ctx = {
        "task_headers": TaskPresenter.build_columns(),
        "tasks": viewmodel
    }
    return render_template("tasks/dashboard.html", **ctx)


@tasks_bp.route("/", methods=["GET", "POST"])
@tasks_bp.route("/<int:task_id>", methods=["PATCH"])
@login_required
@with_db_session
def tasks(session, task_id=None):

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
                "subtype": "task"
            }
        ), 201