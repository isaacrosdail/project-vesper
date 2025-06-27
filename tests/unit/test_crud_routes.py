
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

    json_data = response.get_json()

    # Assert on the message field
    assert json_data["message"] == "Task deleted"
    assert json_data["success"] == True
    assert response.status_code == 200 # Should now return 200 since we're returning JSON

    # Confirm task no longer exists
    deleted_task = db_session.get(Task, task_id)
    assert deleted_task is None