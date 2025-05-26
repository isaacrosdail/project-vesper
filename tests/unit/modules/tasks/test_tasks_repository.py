from app.core.database import db_session
from app.modules.tasks import repository as tasks_repo
from app.modules.tasks.models import Task


# Empty DB
def test_get_all_tasks_empty():
    tasks = tasks_repo.get_all_tasks(db_session)
    assert tasks == []

# With tasks
def test_get_all_tasks_with_entries():
    task = Task(title="Git Task")
    db_session.add(task)
    db_session.flush()

    tasks = tasks_repo.get_all_tasks(db_session)
    assert len(tasks) == 1
    assert tasks[0].title == "Git Task"