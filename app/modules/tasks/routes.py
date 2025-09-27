
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.api.responses import api_response, validation_failed
from app.modules.tasks.models import PriorityEnum
from app.modules.tasks.repository import TasksRepository
from app.modules.tasks.viewmodels import TaskViewModel, TaskPresenter
from app.shared.datetime.helpers import parse_eod_datetime_from_date
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
@login_required
@with_db_session
def tasks(session):
    if request.method == "POST":
        
        form_data = {
            "name": request.form.get("name", ""),
            "priority": request.form.get("priority", "medium"),
            "due_date": request.form.get("due_date", "")
        }
        
        errors = validate_task(form_data)
        if errors:
            return validation_failed(errors), 400
        
        priority = PriorityEnum(form_data["priority"])
        due_date = (
            parse_eod_datetime_from_date(form_data["due_date"], current_user.timezone)
            if form_data["due_date"]
            else None
        )
        is_frog = bool(request.form.get("is_frog"))

        tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
        task = tasks_repo.create_task(
            name=form_data["name"],
            priority=priority,
            is_frog=is_frog,
            due_date=due_date
        )

        return api_response(
            True,
            "Task added successfully",
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