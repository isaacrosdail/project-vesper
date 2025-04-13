
def test_task_creation_and_completion(client, db_session):
    # 1. Add new task
    response = client.post("/tasks/add_task", data={"title": "Integration Task"})
    assert response.status_code == 302 # Expect redirect

    # Fetch from DB
    from app.modules.tasks.models import Task
    task = db_session.query(Task).filter_by(title="Integration Task").first()
    assert task is not None
    assert task.is_done is False

    # Mark it complete
    response = client.post(f"/tasks/complete_task/{task.id}")
    assert response.status_code == 200
    assert response.json["success"] is True

    db_session.expire_all() # Ensure fresh read from DB
    updated_task = db_session.get(Task, task.id)
    assert updated_task.is_done is True
    assert updated_task.completed_at is not None
    
    # Ensure that dashboard displays it
    response = client.get("/tasks/")
    assert b"Integration Task" in response.data