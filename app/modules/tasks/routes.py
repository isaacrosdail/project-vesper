
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.modules.tasks.repository import TasksRepository
from app.modules.tasks.viewmodels import TaskPresenter, TaskViewModel
from app.shared.decorators import login_plus_session
from app.shared.collections import sort_by_field


tasks_bp = Blueprint('tasks', __name__, template_folder="templates", url_prefix="/tasks")

@tasks_bp.route("/dashboard", methods=["GET"])
@login_plus_session
def dashboard(session: 'Session') -> Any:

    tasks_sort = request.args.get("tasks_sort", "name")
    tasks_order = request.args.get("tasks_order", "desc")

    tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
    tasks = tasks_repo.get_all()
    tasks = sort_by_field(tasks, tasks_sort, tasks_order)
    
    viewmodel = [TaskViewModel(t, current_user.timezone) for t in tasks]

    ctx = {
        "task_headers": TaskPresenter.build_columns(),
        "tasks": viewmodel,
        "tasks_sort": tasks_sort,
        "tasks_order": tasks_order,
    }
    return render_template("tasks/dashboard.html", **ctx)
