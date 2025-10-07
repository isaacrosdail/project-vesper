
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import HabitsService
from app.modules.habits.viewmodels import HabitPresenter, HabitViewModel


habits_bp = Blueprint('habits', __name__, template_folder="templates", url_prefix="/habits")


@habits_bp.route("/dashboard", methods=["GET"])
@login_required
@with_db_session
def dashboard(session):
    
    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    habits = habits_repo.get_all_habits_and_tags()

    viewmodels = [HabitViewModel(h, current_user.timezone) for h in habits]
    ctx = {
        "headers": HabitPresenter.build_columns(),
        "habits": viewmodels
    }
    return render_template("habits/dashboard.html", **ctx)
