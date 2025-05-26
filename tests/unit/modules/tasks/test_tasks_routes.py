import pytest
from app.modules.tasks.models import Task
from app.core.database import db_session
from datetime import datetime, timezone, timedelta

# Create test task in the DB for use in tests
@pytest.fixture
def sample_task(db_session):
    task = Task(title="Test Task")
    db_session.add(task)
    db_session.flush() # Flush to DB without committing
    return task

# region dashboard tests
def test_tasks_dashboard_loads(client):
    response = client.get("/tasks/")
    assert response.status_code == 200
    # TODO: Add language toggle assertion when implemented
    # assert b"Tasks" in response.data

# Test that tasks are visible on dashboard after creation
def test_tasks_dashboard_displays_tasks(client):
    # Create task via form submission (Avoids session isolation issues)
    response = client.post("/tasks/add", data={"title": "Visible Task"})
    assert response.status_code == 302 # Redirect after successful creation

    # Verify task appears on dashboard
    response = client.get("/tasks/")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Visible Task" in html
# endregion

# Test GET (add task form page loads correctly)
def test_add_task_form_loads(client):
    response = client.get("/tasks/add")
    assert response.status_code == 200
    assert "Add new task" in response.get_data(as_text=True)

# Test POST (submitting add task form creates a new task in the database)
def test_add_task_creates_task(client):
    response = client.post("/tasks/add", data={"title": "From Test"})
    assert response.status_code == 302 # Redirect after successful creation

    # Verify task was created in database
    task = db_session.query(Task).filter_by(title="From Test").first()
    assert task is not None
    assert task.is_done is False # Verify default state

# Test marking a task as complete via PATCH request (in index.html JS function)
def test_complete_task(client):

    # Create task to test completion
    response = client.post("/tasks/add", data={"title": "Complete Me"})
    assert response.status_code == 302 # Redirect after success

    # Get task ID from database
    session = db_session()
    task = session.query(Task).filter_by(title="Complete Me").first()
    task_id = task.id # Grab ID, don't reuse instance

    # Test task completion via PATCH request
    response = client.patch(
        f"/tasks/{task_id}",
        json={"is_done": True})
    assert response.status_code == 200
    assert response.json["success"] is True

    # Verify task state was updated
    updated_task = session.get(Task, task_id)
    assert updated_task.is_done is True
    assert updated_task.completed_at is not None
    assert abs(updated_task.completed_at - datetime.now(timezone.utc)) < timedelta(minutes=1)