"""Tests for the raw-SQL wipe helpers in app.shared.database.helpers.
"""
from datetime import date

from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session

# from app._infra.database import db_session
from app.api.models import ApiCallRecord
from app.modules.auth.models import User, UserGoals, UserProfile
from app.modules.auth.repository import UsersRepository
from app.modules.auth.schemas import UserRegister
from app.modules.auth.service import AuthService
from app.modules.habits.models import Habit
from app.modules.tasks.models import PriorityEnum, Task
from app.shared.database.helpers import (
    delete_all_db_data,
    delete_user_activity_data,
    user_scoped_tables,
)

ACCOUNT_TABLES = {"user_goals", "user_profiles"}


def row_count_by_table(session: Session, user_id: int) -> dict[str, int]:
    return {
        t.name: session.scalar(select(func.count()).select_from(t).where(t.c.user_id == user_id)) or 0
        for t in user_scoped_tables()
    }

def make_habit(user_id: int) -> Habit:
    return Habit(name="test habit", target_frequency=4, user_id=user_id)


def test_activity_wipe_scoped_to_user(session, logged_in_user, second_logged_in_user):
    # Arrange: add two users, each with a couple of rows in two/three tables
    task1 = Task(user_id=logged_in_user.id, name="task1", priority=PriorityEnum.LOW, sort_key="a0")
    task2 = Task(user_id=logged_in_user.id, name="task2", priority=PriorityEnum.MEDIUM, sort_key="a0")

    task3 = Task(user_id=second_logged_in_user.id, name="task3", priority=PriorityEnum.LOW, sort_key="a0")
    task4 = Task(user_id=second_logged_in_user.id, name="task4", priority=PriorityEnum.MEDIUM, sort_key="a0")

    session.add_all([task1, task2, task3, task4])
    session.flush()

    delete_user_activity_data(session, logged_in_user.id)

    # User A: activity gone, account structure intact
    a = row_count_by_table(session, logged_in_user.id)
    assert not any(v for k, v in a.items() if k not in ACCOUNT_TABLES)
    assert all(a[k] == 1 for k in ACCOUNT_TABLES)

    # User B untouched, both account survive
    b = row_count_by_table(session, second_logged_in_user.id)
    assert b["tasks"] == 2
    assert session.scalar(select(func.count()).select_from(User)) == 2


def test_never_delete_tables_survive_wipe(session, logged_in_user):
    # Seed rows
    record = ApiCallRecord(api_called="test", date=date(2026, 5, 5), call_count=5)
    habit = Habit(name="Pending habit", target_frequency=5, user_id=logged_in_user.id)
    session.add_all([record, habit])

    # At this point, selects trigger autoflush, so both are .persistent
    result = session.scalar(select(ApiCallRecord).where(ApiCallRecord.api_called=="test"))
    assert result is record
    assert session.scalar(select(Habit).where(Habit.user_id==logged_in_user.id))
    assert all(inspect(obj).persistent for obj in [record, habit])

    # Wipe with users
    delete_all_db_data(session, include_users=True)

    # Prevent autoflush so the assert cannot insert what it checks
    with session.no_autoflush:
        assert session.scalar(select(func.count()).select_from(ApiCallRecord)) == 1
        assert session.scalar(select(func.count()).select_from(Habit)) == 0


## 8. Flush regression: add habit w/o flushing, call del user data, assert count for user's habits is 0
#   delete teh session.flush() line in delete_user_Activity_data and this should fail
def test_user_wipe_flushes_pending_first(session, logged_in_user):
    # Add item to the session WITHOUT flushin
    # Remove session.flush() from delete_user_activity_data and this fails.
    habit = make_habit(logged_in_user.id)
    session.add(habit)
    assert inspect(habit).pending

    delete_user_activity_data(session, logged_in_user.id)

    # Autoflush live on purpose: a leaked pending habit would flush in NOW,
    # after the wipe, and the count of 1 exposes it.
    assert session.scalar(select(func.count()).select_from(Habit).where(Habit.user_id==logged_in_user.id)) == 0


## 9. Expire regression: create a task, _touch_ logged_in_user.tasks so the relationship collection loads, wipe, then
#  assert logged_in_user.tasks == []. W/o expire_all(), the loaded collection still holds the ghost task and the assert fails.
def test_user_wipe_expires_loaded_state(session, logged_in_user):
    # Create a habit
    # Remove expire_all() from delete_user_activity_data and this fails.
    user = session.get(User, logged_in_user.id)
    habit = make_habit(logged_in_user.id)
    user.habits.append(habit)
    session.flush()
    assert user.habits == [habit] # relationship collection is loaded in memory

    delete_user_activity_data(session, user.id)
    # Without expire_all(), the loaded collection would still be [habit]
    assert user.habits == []

def test_sequences_reset_for_empty_tables(session, logged_in_user):
    delete_all_db_data(session, include_users=False, reset_sequences=True)

    # First habit after reset's sequence should reset, now starting again at 1
    habit = make_habit(logged_in_user.id)
    session.add(habit)
    session.flush()
    assert habit.id == 1

## 6. seed activity for a user, wipe, assert profile+goals rows sstill exist AND tasks/habits/etc are 0
def test_activity_wipe_preserves_account_structure(session, logged_in_user):
    habit = make_habit(logged_in_user.id)
    session.add(habit)
    assert inspect(habit).pending

    delete_user_activity_data(session, logged_in_user.id)

    ## Assert profile+goals rows still exist and the rest are count 0
    assert session.scalar(select(func.count()).select_from(UserProfile).where(UserProfile.user_id==logged_in_user.id)) == 1
    assert session.scalar(select(func.count()).select_from(UserGoals).where(UserGoals.user_id==logged_in_user.id)) == 1
    assert session.scalar(select(func.count()).select_from(Habit).where(Habit.user_id==logged_in_user.id)) == 0


def test_users_survive_delete_all_include_users_false(session, logged_in_user, second_logged_in_user):
    session.add(make_habit(logged_in_user.id))
    assert session.scalar(select(func.count()).select_from(Habit)) == 1
    # Easy: delete with flag false, see if both our fixtures survive
    delete_all_db_data(session, include_users=False)

    # Both users, no habit entries
    assert session.scalar(select(func.count()).select_from(Habit)) == 0
    assert session.scalar(select(func.count()).select_from(User)) == 2

## 2. Users deleted when incl users is true
def test_users_deleted_when_include_users_true(session, logged_in_user):
    assert session.scalar(select(func.count()).select_from(User)) > 0

    delete_all_db_data(session, include_users=True)

    assert session.scalar(select(func.count()).select_from(User)) == 0

def test_sequences_without_users(session, logged_in_user, second_logged_in_user):
    # register a third user -> should succeed
    auth_service = AuthService(session, UsersRepository(session))
    validated = UserRegister(username="testusername", password="testpassword", name=None, timezone="America/Chicago") #noqa: S106
    user = auth_service.register_user(validated)

    # User table is not wiped, therefore its sequence is not reset either
    assert user.id == second_logged_in_user.id + 1
