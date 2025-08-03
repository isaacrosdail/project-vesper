from app.core.database import db_session
from app.modules.tasks.repository import get_user_tasks
from app.modules.tasks.models import Task


# Empty DB
def test_get_user_tasks_empty(logged_in_user):
    tasks = get_user_tasks(db_session, logged_in_user.id)
    assert tasks == []

# With tasks
def test_get_all_tasks_with_entries(logged_in_user):
    task = Task(title="Git Task", user_id=logged_in_user.id)
    db_session.add(task)
    db_session.flush()

    tasks = get_user_tasks(db_session, logged_in_user.id)
    assert len(tasks) == 1
    assert tasks[0].title == "Git Task"