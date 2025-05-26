from app.core.database import db_session


def test_task_creation_and_completion(client):
    # 1. Add new task
    response = client.post("/tasks/add", data={"title": "Integration Task"})
    assert response.status_code == 302 # Expect redirect

    # Fetch from DB
    from app.modules.tasks.models import Task
    task = db_session.query(Task).filter_by(title="Integration Task").first()
    task_id = task.id
    assert task is not None
    assert task.is_done is False

    # Mark task complete via PATCH to update_task route
    response = client.patch(f"/tasks/{task_id}",
                            json={"is_done": True})
    assert response.status_code == 200
    assert response.json["success"] is True

    updated_task = db_session.get(Task, task_id)
    assert updated_task.is_done is True
    assert updated_task.completed_at is not None
    
    # Ensure that dashboard displays it
    response = client.get("/tasks/")
    assert b"Integration Task" in response.data