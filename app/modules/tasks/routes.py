
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.tasks.models import Priority
from app.modules.tasks.repository import TasksRepository
from datetime import datetime, time
from zoneinfo import ZoneInfo
from app.modules.tasks.viewmodels import TaskViewModel, TaskPresenter

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
        # Parse form data
        due_date_str = request.form.get("due_date")
        # TODO: Hacky & gross, should move this to a helper or something
        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            end_of_day_time = time(23, 59, 59)
            due_datetime = datetime.combine(due_date, end_of_day_time)
            due_datetime_aware = due_datetime.replace(tzinfo=ZoneInfo(current_user.timezone))
        else:
            due_datetime_aware = None
        priority = Priority(request.form.get("priority", "medium"))
        is_frog = bool(request.form.get("is_frog"))
        tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
        new_task = tasks_repo.create_task(
            name=request.form.get("name"),
            priority=priority,
            is_frog=is_frog,
            due_date=due_datetime_aware
        )

        return jsonify({
            "success": True, 
            "message": "Task added successfully.",
            "task": {
                "id": new_task.id,
                "name": new_task.name
            }
        }), 200