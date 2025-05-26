
from app.core.database import db_session

# Import model(s)
from app.modules.tasks.models import Task

# Test DELETE functionality for generalized crud routes
def test_general_delete_task(client):
    # Create test task
    task = Task(title="Mock delete-me-task")
    db_session.add(task)
    db_session.commit()

    task_id = task.id

    # DELETE request to route
    response = client.delete(f"/tasks/none/{task_id}")

    # Check response code
    assert response.status_code == 204 # 204 No Content (success for delete)

    # Confirm task no longer exists
    deleted_task = db_session.get(Task, task_id)
    assert deleted_task is None