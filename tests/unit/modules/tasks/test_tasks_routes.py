
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

def test_tasks_dashboard_loads(authenticated_client):
    response = authenticated_client.get("/tasks/dashboard")
    assert response.status_code == 200

# Test that tasks are visible on dashboard after creation
def test_tasks_dashboard_displays_tasks(authenticated_client):
    # TODO: NOTES: Create task via form submission (Avoids session isolation issues)
    response = authenticated_client.post("/tasks/", data={"title": "Visible Task"})
    assert response.status_code == 200 # Successful CREATE
    
    # Verify task appears on dashboard
    response = authenticated_client.get("/tasks/dashboard")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Visible Task" in html