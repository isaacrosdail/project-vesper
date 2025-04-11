import pytest
from app.modules.tasks.models import Task
from datetime import datetime, timezone, timedelta

# Fixture to create a test task
# This adds & commits to in memory db, letting us just pass sample_task in
# to any test then we have access to 'task' directly! :P
@pytest.fixture
def sample_task(db_session):
    task = Task(title="Test Task") # required field only
    db_session.add(task)
    db_session.commit()
    return task

def test_sample_task_is_created(db_session, sample_task):
    assert sample_task is not None
    assert sample_task.title == "Test Task"
    assert sample_task.is_done is False

def test_complete_task(client, db_session, sample_task):
    # To test: is_done = True, completed_at is set correctly, Route returns {"success": True}
    # Assumes we have:
    # A Task model
    # A working client fixture
    # A working db_session fixture
    # Route exists in Flask: /complete_task/<task_id>, method: POST

    print(f"Session in test: {id(db_session)}")
    response = client.post(f"/complete_task/{sample_task.id}")

    assert response.status_code == 200
    assert response.json["success"] is True

    # Fetch from DB to be sure
    db_session.expire_all() # Invalidates everything cached so we see the real DB values
    updated_task = db_session.get(Task, sample_task.id)
    assert updated_task.is_done is True
    assert updated_task.completed_at is not None
    assert abs(sample_task.completed_at - datetime.now(timezone.utc)) < timedelta(minutes=1)