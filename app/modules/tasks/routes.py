
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.modules.tasks.service import create_tasks_service
from app.modules.tasks.viewmodels import TaskPresenter, TaskViewModel
from app.shared.decorators import login_plus_session
from app.shared.collections import sort_by_field
from app.shared.parsers import get_table_params


tasks_bp = Blueprint('tasks', __name__, template_folder="templates", url_prefix="/tasks")

@tasks_bp.get("/dashboard")
@login_plus_session
def dashboard(session: 'Session') -> tuple[str, int]:
    tasks_params = get_table_params('tasks', 'due_date')

    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)
    tasks = tasks_service.task_repo.get_all()
    tasks = sort_by_field(tasks, tasks_params['sort_by'], tasks_params['order'])
    
    viewmodel = [TaskViewModel(t, current_user.timezone) for t in tasks]

    ctx = {
        "tasks_params": tasks_params,
        "task_headers": TaskPresenter.build_columns(),
        "tasks": viewmodel,
    }
    return render_template("tasks/dashboard.html", **ctx), 200
