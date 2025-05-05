import pytest
from app.modules.tasks.models import Task
from app.core.database import db_session
from datetime import datetime, timezone, timedelta
import time
# Fixture to create a test task
# This adds & commits to in memory db, letting us just pass sample_task in
# to any test then we have access to 'task' directly! :P
@pytest.fixture
def sample_task(db_session):
    task = Task(title="Test Task") # required field only
    db_session.add(task)
    db_session.flush() # instead of commit
    return task

# region dashboard
def test_tasks_dashboard_loads(client):
    response = client.get("/tasks/")
    assert response.status_code == 200
    # assert b"Tasks" in response.data ## ADD THIS WHEN WE INTEGRATE LANGUAGE TOGGLE

def test_tasks_dashboard_displays_tasks(client):
    # Simulate real user adding task via form (Avoids cross-session visibility issues)
    response = client.post("/tasks/add", data={"title": "Visible Task"})
    assert response.status_code == 302 # Confirm redirect after success

    # Check dashboard route for task
    response = client.get("/tasks/")
    html = response.get_data(as_text=True)
    print(html)

    assert response.status_code == 200
    assert "Visible Task" in html
# endregion

# Test GET
def test_add_task_form_loads(client):
    response = client.get("/tasks/add")
    assert response.status_code == 200
    assert "Add new task" in response.get_data(as_text=True)

# Test POST
def test_add_task_creates_task(client):
    response = client.post("/tasks/add", data={"title": "From Test"})
    assert response.status_code == 302 # Redir after successful POST

    # Check DB to confirm
    task = db_session.query(Task).filter_by(title="From Test").first()
    assert task is not None
    assert task.is_done is False # Default behavior check

# Test marking an anchor_habit (task) as complete via the checkbox on home & JS function
def test_complete_task(client):
    # To test: is_done = True, completed_at is set correctly
    # Route returns {"success": True}

    # Create task via actual route
    response = client.post("/tasks/add", data={"title": "Complete Me"})
    assert response.status_code == 302 # Redirect after success

    # Fetch task from DB to get ID
    session = db_session()
    task = session.query(Task).filter_by(title="Complete Me").first()
    task_id = task.id # Grab ID, don't reuse instance

    # Now test the real completion route
    response = client.patch(
        f"/tasks/{task_id}",
        json={"is_done": True})
    assert response.status_code == 200
    assert response.json["success"] is True

    # Fetch again & assert changes
    updated_task = session.get(Task, task_id)
    assert updated_task.is_done is True
    assert updated_task.completed_at is not None
    assert abs(updated_task.completed_at - datetime.now(timezone.utc)) < timedelta(minutes=1)