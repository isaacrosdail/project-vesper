


import pytest
from pydantic import ValidationError

from app.modules.tasks.models import PriorityEnum
from app.modules.tasks.schemas import TaskCreate


def test_create_frog_no_due_date_rejects_400():
    with pytest.raises(ValidationError, match="Frog tasks must have a due date"):
        TaskCreate(name="Test", priority=PriorityEnum.FROG)

## Problem: TaskPatch allows explicit null on three not null cols:
#   name, priority, sort_key
## TODO: rewrite to pure schema test?
@pytest.mark.parametrize("field", ["name", "priority", "sort_key"])
def test_patch_explicit_null_on_required_field_returns_400(authenticated_client, field):
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Original", "priority": "low",
    })
    task_id = create.json["data"]["id"]

    resp = authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={field: None})
    assert resp.status_code == 400
