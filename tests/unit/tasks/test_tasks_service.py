
from datetime import date, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.exc import IntegrityError

from app._infra.database import db_session
from app.modules.tasks.models import PriorityEnum
from app.modules.tasks.schemas import TaskCreate, TaskPatch
from app.modules.tasks.service import create_tasks_service
from app.shared.datetime_ import helpers as dth
from app.shared.exceptions import ServiceError


@pytest.fixture
def service(logged_in_user):
    return create_tasks_service(db_session, logged_in_user.id, logged_in_user.timezone)


def test_create_frog_duplicate_on_same_due_datetime_service_error(service):
    # Create first frog on date A
    validated = TaskCreate(name="Test", priority=PriorityEnum.FROG, due_datetime="2026-08-08T00:00:00Z")
    task = service.create_task(validated)

    # Create second on date A, asserting raises ServiceError
    validated_two = TaskCreate(name="TestDupe", priority=PriorityEnum.FROG, due_datetime="2026-08-08T00:00:00Z")
    with pytest.raises(ServiceError, match="Pre-existing 'frog' task for "):
        service.create_task(validated_two)


def test_create_frog_valid():
    pass

def test_patch_frog_name_does_not_trip_preexisting_frog_check(service):
    # Create first frog on date A
    validated = TaskCreate(name="Test", priority=PriorityEnum.FROG, due_datetime="2026-08-08T00:00:00Z")
    task = service.create_task(validated)

    patch = TaskPatch(name="TestNewName")
    service.update_task(task.id, patch)


def test_patch_priority_to_frog_with_no_due_datetime_raises(service):
    # Create first frog on date A
    validated = TaskCreate(name="Test", priority=PriorityEnum.LOW)
    task = service.create_task(validated)

    patch = TaskPatch(priority=PriorityEnum.FROG)
    with pytest.raises(ServiceError, match="Frog tasks must have a due date"):
        service.update_task(task.id, patch)

def test_patch_remove_due_datetime_on_frog_rejects(service):
    # Create first frog on date A
    validated = TaskCreate(name="Test", priority=PriorityEnum.FROG, due_datetime="2026-08-08T00:00:00Z")
    task = service.create_task(validated)

    patch = TaskPatch(due_datetime=None)
    with pytest.raises(ServiceError, match="Frog tasks must have a due date"):
        service.update_task(task.id, patch)


## Problem: TaskPatch allows explicit null on three not null cols:
#   name, priority, sort_key
def test_patch_frog_onto_task_with_due_datetime_accepts(service):
    # Create then patch
    validated = TaskCreate(name="Original", priority=PriorityEnum.LOW, due_datetime="2026-08-08T00:00:00Z")
    task = service.create_task(validated)

    patch = TaskPatch(priority=PriorityEnum.FROG)
    service.update_task(task.id, patch)

## does this one even make any sense?
def test_patch_only_updates_sent_fields(authenticated_client):
    """Patch name shouldn't wipe priority."""
    create = authenticated_client.post("/api/tasks/tasks", json={
        "name": "Original", "priority": "high",
    })
    task_id = create.json["data"]["id"]

    # Only patch name
    authenticated_client.patch(f"/api/tasks/tasks/{task_id}", json={
        "name": "Updated"
    })

    get_all = authenticated_client.get("/api/tasks/tasks")
    task = next(t for t in get_all.json["data"] if t["id"] == task_id)
    assert task["name"] == "Updated"
    assert task["priority"] == "high"  # should NOT be wiped


def test_patch_clear_due_datetime_on_non_frog_works(service):
    validated = TaskCreate(name="Original", priority=PriorityEnum.LOW, due_datetime="2026-08-08T00:00:00Z")
    task = service.create_task(validated)

    patch = TaskPatch(due_datetime=None)
    service.update_task(task.id, patch)

    task = service.get_task(task.id)
    assert task.due_datetime is None


def test_thing(service):
    ## Create a task with a due_datetime whose UTC calendar date differs from the user's local calendar date, assert which
    #   day it lands on. EX: A client sending 2026-07-16T04:00Z meaning "11pm July 15 Chicago" gets EOD of July 16, not 15.
    ## 11:00pm Jul 15 in Chicago -> "due July 15" -> UTC calendar date 16th
    validated = TaskCreate(name="Test", priority=PriorityEnum.MEDIUM, due_datetime="2026-07-16T04:00:00Z")
    task = service.create_task(validated)

    local_due = task.due_datetime.astimezone(ZoneInfo("America/Chicago"))
    assert local_due.date() == date(2026, 7, 15)
    assert local_due.time() == time(23, 59, 59)


def test_frogs_on_adjacent_local_days_both_allowed(service):
    ## Frog due 23:30 local, attempt second frog at 00:30 next day, should succeed.
    # Both are Jul 16 in UTC. Chicago: 11:30pm Jul 15 vs 12:30am Jul 16.
    # Difference local days, so both are legal.
    service.create_task(
        TaskCreate(name="Frog A", priority=PriorityEnum.FROG, due_datetime="2026-07-16T04:30:00Z")
    )
    task_b = service.create_task(
        TaskCreate(name="Frog B", priority=PriorityEnum.FROG, due_datetime="2026-07-16T05:30:00Z")
    )
    assert task_b.is_frog

def test_frogs_thing(service):
    ## False negative: Both due Jul 15 Chicago-local but on diff UTC calendar dates: second should reject
    first = TaskCreate(name="Frog A", priority=PriorityEnum.FROG, due_datetime="2026-07-15T23:00:00Z")
    service.create_task(first)

    second = TaskCreate(name="Frog B", priority=PriorityEnum.FROG, due_datetime="2026-07-16T04:30:00Z")
    with pytest.raises(ServiceError):
        service.create_task(second)


def test_partial_unique_index():
    # two open tasks, same name, same user: rejected.
    # create a task named the same as a completed task: succeeds.
    pass

def test_partial_unique_index_two(service):
    # complete task X, create a new open X, then patch completed_at: null on the old one. IntegrityError at flush.
    #   Test what the API actually returns. If it's a raw 500 -> thats a missing IntegrityError.
    t1 = service.create_task(TaskCreate(name="Task A", priority=PriorityEnum.LOW))
    patch = TaskPatch(completed_at="2026-07-16T04:30:00Z")
    service.update_task(t1.id, patch)
    assert t1.completed_at is not None

    # Create new open X
    t2 = service.create_task(TaskCreate(name="Task A", priority=PriorityEnum.LOW))
    # Patch completed_at null on the old one: service accepts
    patch2 = TaskPatch(completed_at=None)
    service.update_task(t1.id, patch2)

    # Partial index rejects at flush time
    with pytest.raises(IntegrityError):
        service.session.flush()


def test_patch_subtask_ids_cycle(service):
    # Patch subtask_ids containing the task's own id: rejected via cycle check.
    validated = TaskCreate(name="Task", priority=PriorityEnum.LOW)
    task = service.create_task(validated)

    patch = TaskPatch(name="Task B", priority=PriorityEnum.LOW, subtask_ids=[task.id])
    with pytest.raises(ServiceError, match="Cycle in links! Rejecting link add"):
        service.update_task(task.id, patch)


def test_reject_cycle(service):
    # A->B, then B->C, then patch C to have subtask A: rejected as a cycle.
    task_c = service.create_task(TaskCreate(name="C", priority=PriorityEnum.LOW))
    task_b = service.create_task(TaskCreate(name="B", priority=PriorityEnum.LOW, subtask_ids=[task_c.id]))
    task_a = service.create_task(TaskCreate(name="A", priority=PriorityEnum.LOW, subtask_ids=[task_b.id]))

    patch = TaskPatch(subtask_ids=[task_a.id])
    with pytest.raises(ServiceError):
        service.update_task(task_c.id, patch)

def test_patch_subtask_ids_empty_list_clears_links(service):
    # Patch subtask_ids: [] removes all existing links.
    # Set up first tasks
    t1 = service.create_task(TaskCreate(name="Task 1", priority=PriorityEnum.LOW))
    t2 = service.create_task(TaskCreate(name="Task 2", priority=PriorityEnum.LOW))
    t3 = service.create_task(TaskCreate(name="Task 3", priority=PriorityEnum.LOW))

    validated = TaskCreate(name="Task with subtasks", priority=PriorityEnum.LOW, subtask_ids=[t1.id, t2.id, t3.id])
    task_create = service.create_task(validated)

    assert task_create.subtasks == [t1, t2, t3]

    # Then clear and assert empty
    patch = TaskPatch(subtask_ids=[])
    patched = service.update_task(task_create.id, patch)

    assert patched.subtasks == []


def test_subtask_ids_containing_nonexistent_id_404s(service):
    validated = TaskCreate(name="Task", priority=PriorityEnum.LOW, subtask_ids=[3,4,5])
    with pytest.raises(ServiceError, match="Sub/super task not found"):
        service.create_task(validated)

def test_same_task_as_subtask_and_supertask_rejected(service):
    # Task T with subtask_ids: [X] and supertask_ids: [X] in the same payload. Reading save_link, the
    #  second link gets rejected with "Link already exists", which is the wrong message for what's really a 2-cycle?
    t1 = service.create_task(TaskCreate(name="t1", priority=PriorityEnum.LOW))
    t2 = service.create_task(TaskCreate(name="t2", priority=PriorityEnum.LOW))

    patch = TaskPatch(subtask_ids=[t1.id], supertask_ids=[t1.id])
    with pytest.raises(ServiceError):
        service.update_task(t2.id, patch)


# Rates and progress
# - calculate_tasks_progress_today with zero tasks in the pile: {0, 0, 0}, no ZeroDivisionError.
# - Overdue-but-open task from last week counts in today's pile denominator.
# - Task completed today with no due_datetime counts in the pile.
# - Percent truncation: 1 of 3 done gives 33, not 33.33.
# - calc_overdue_rate with no tasks in window: rate 0.
# - calc_frog_adherence_rate: frog completed after its due_datetime counts as not-done. Late completion is the interesting branch at
# line 248.

def test_progress_pile_membership_and_truncation(service):
    now = dth.now_utc()

    # In pile: overdue-open from last week
    service.create_task(TaskCreate(name="Overdue", priority=PriorityEnum.LOW, due_datetime=now - timedelta(days=7)))
    # In pile: due today, still open
    service.create_task(TaskCreate(name="DueToday", priority=PriorityEnum.LOW, due_datetime=now))
    # In pile: completed today, never had a due date
    done = service.create_task(TaskCreate(name="DoneToday", priority=PriorityEnum.LOW))
    service.update_task(done.id, TaskPatch(completed_at=now))
    # NOT in pile: open, due next week
    service.create_task(TaskCreate(name="Future", priority=PriorityEnum.LOW, due_datetime=now + timedelta(days=7)))

    # 1 of 3 done — and 33, not 34: int() truncates
    assert service.calculate_tasks_progress_today() == {"completed": 1, "total": 3, "percent": 33}

def test_overdue_rate_empty_window(service):
    assert service.calc_overdue_rate(days=7) == {"rate": 0, "overdue": 0, "total": 0}

def test_frog_adherence_late_completion_is_a_miss(service):
    now = dth.now_utc()

    late = service.create_task(TaskCreate(name="Frog late", priority=PriorityEnum.FROG, due_datetime=now - timedelta(days=3)))
    service.update_task(late.id, TaskPatch(completed_at=now)) # finished after due

    ontime = service.create_task(TaskCreate(name="Frog on time", priority=PriorityEnum.FROG, due_datetime=now - timedelta(days=2)))
    service.update_task(ontime.id, TaskPatch(completed_at=now - timedelta(days=2, hours=12)))

    assert service.calc_frog_adherence_rate(days=7) == {"rate": 50, "done": 1, "total": 2}
