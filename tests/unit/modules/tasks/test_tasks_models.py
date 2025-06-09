from app.core.database import db_session
from app.modules.tasks.models import Task


def test_insert_and_query_task(app):
    session = db_session()
    task = Task(title="Test Task", type="todo")
    session.add(task)
    session.flush() # instead of commit

    result = session.query(Task).filter_by(
        title="Test Task"
    ).first()
    
    assert result.type == "todo"
    session.close()