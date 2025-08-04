
import pytest

from app.core.database import db_session, database_connection
from app.modules.tasks.models import Task


# Create test task in the DB for use in tests
@pytest.fixture
def sample_task(db_session, logged_in_user):
    task = Task(title="Test Task", user_id=logged_in_user.id)
    db_session.add(task)
    db_session.flush() # Flush to DB without committing
    return task

# region dashboard tests
def test_tasks_dashboard_loads(authenticated_client):
    response = authenticated_client.get("/tasks/")
    assert response.status_code == 200
    # TODO: Add language toggle assertion when implemented
    # assert b"Tasks" in response.data

# Test that tasks are visible on dashboard after creation
def test_tasks_dashboard_displays_tasks(authenticated_client):
    # Create task via form submission (Avoids session isolation issues)
    response = authenticated_client.post("/tasks/", data={"title": "Visible Task"})
    assert response.status_code == 302 # Redirect after successful creation

    # Verify task appears on dashboard
    response = authenticated_client.get("/tasks/dashboard")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Visible Task" in html
# endregion

# Test GET (add task form page loads correctly)
def test_add_task_form_loads(authenticated_client):
    response = authenticated_client.get("/tasks/")

    assert response.status_code == 200
    assert "Add new task" in response.get_data(as_text=True)

# Test POST (submitting add task form creates a new task in the database)
def test_add_task_creates_task(authenticated_client):
    response = authenticated_client.post("/tasks/", data={"title": "From Test"})
    assert response.status_code == 302 # Redirect after successful creation

    # Verify task was created in database
    with database_connection() as session:
        task = db_session.query(Task).filter_by(title="From Test").first()
        assert task is not None
        assert task.is_done is False # Verify default state
