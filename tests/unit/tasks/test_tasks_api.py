
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app._infra.database import db_session
from app.modules.tasks.models import Task


def test_validation_error_400_envelope_representative(authenticated_client):
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Original", "priority": "low",
    })
    task_id = create.json["data"]["id"]

    resp = authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={"priority": None})
    assert resp.status_code == 400


def test_patch_due_datetime_to_none_on_existing_frog_raises(authenticated_client):
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Original", "priority": "frog", "due_datetime": datetime(2026, 8, 8, tzinfo=ZoneInfo("UTC"))
    })
    task_id = create.json["data"]["id"]

    resp = authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "due_datetime": None,
    })
    assert resp.status_code == 400
    assert resp.json["message"] == "Frog tasks must have a due date"

    task = db_session.execute(select(Task).where(Task.id==task_id)).scalar_one()
    assert task.due_datetime is not None

def test_patch_task_pillars(authenticated_client):
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Test task", "priority": "low",
    })
    task_id = create.json["data"]["id"]

    # Use actual pillar IDs from the seeded data
    response = authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "pillar_ids": [1, 2]  # might need to adjust based on actual IDs
    })
    assert response.status_code == 200
    assert len(response.json["data"]["pillars"]) == 2


def test_create_task(authenticated_client):
    response = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Test task", "priority": "medium",
    })
    assert response.status_code == 201
    assert response.json["data"]["name"] == "Test task"
    ## check progress?
    assert response.json["data"]["progress"]

def test_get_all_tasks(authenticated_client):
    # Create one first
    authenticated_client.post("/api/tasks/tasks", json={
        "name": "Task 1", "priority": "low",
    })
    response = authenticated_client.get("/api/tasks/tasks")
    assert response.status_code == 200
    assert len(response.json["data"]) >= 1


def test_delete_task(authenticated_client):
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "To delete", "priority": "low",
    })
    task_id = create.json["data"]["id"]
    response = authenticated_client.delete(f"/api/tasks/tasks/{task_id}")
    assert response.status_code == 200


def test_create_task_with_pillars_roundtrip(authenticated_client):
      """Create task, add pillars, fetch it back, verify pillars persist."""
      create = authenticated_client.post("/api/tasks/tasks", json={
          "name": "Pillar test", "priority": "high",
      })
      task_id = create.json["data"]["id"]
      authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
          "pillar_ids": [1, 2]
      })

      get_all = authenticated_client.get("/api/tasks/tasks")
      task = next(t for t in get_all.json["data"] if t["id"] == task_id)
      assert len(task["pillars"]) == 2


def test_toggle_complete_roundtrip(authenticated_client):
    """Complete a task, verify it sticks."""
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Toggle test", "priority": "low",
    })
    task_id = create.json["data"]["id"]
    assert not create.json["data"]["is_done"]
    authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "completed_at": "2026-03-20T12:00:00Z"
    })

    task = authenticated_client.get(f"/api/tasks/tasks/{task_id}")
    assert task.json["data"]["is_done"]


def test_uncomplete_task(authenticated_client):
    """Complete then uncomplete a task."""
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Uncomplete test", "priority": "low",
    })
    task_id = create.json["data"]["id"]

    authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "completed_at": "2026-03-20T12:00:00Z"
    })
    authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "completed_at": None
    })

    get_all = authenticated_client.get("/api/tasks/tasks")
    task = next(t for t in get_all.json["data"] if t["id"] == task_id)
    assert not task["is_done"]


def test_remove_pillars(authenticated_client):
    """Add pillars then remove them."""
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Remove pillars test", "priority": "low",
    })
    task_id = create.json["data"]["id"]

    # Add
    authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "pillar_ids": [1,2]
    })
    get_all = authenticated_client.get("/api/tasks/tasks")
    task = next(t for t in get_all.json["data"] if t["id"] == task_id)
    assert len(task["pillars"]) != 0
    # Remove (empty string = no pillars)
    authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "pillar_ids": []
    })

    get_all = authenticated_client.get("/api/tasks/tasks")
    task = next(t for t in get_all.json["data"] if t["id"] == task_id)
    assert len(task["pillars"]) == 0


def test_create_task_invalid(authenticated_client):
    resp = authenticated_client.post("/api/tasks/tasks", json={
        "name": "", "priority": "banana"
    })
    assert resp.status_code == 400
    assert resp.json["code"] == "VALIDATION_ERROR"

def test_patch_task_valid(authenticated_client):
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Original", "priority": "low"
    })
    task_id = create.json["data"]["id"]
    resp = authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "name": "Updated"
    })
    assert resp.status_code == 200
    assert resp.json["data"]["name"] == "Updated"

def test_patch_task_invalid(authenticated_client):
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Original", "priority": "low"
    })
    task_id = create.json["data"]["id"]
    resp = authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "priority": "banana"
    })
    assert resp.status_code == 400

