# Basic script to seed our db with dummy data for demo purposes
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.auth.models import User

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.modules.habits.models import Habit, HabitCompletion
from app.modules.metrics.models import DailyMetrics
from app.modules.tasks.models import PriorityEnum, Task
from app.modules.time_tracking.models import TimeEntry
from app.shared.models import Tag


# Seed appropriate datasets for user type
def seed_data_for(session: Session, user: User) -> None:
    session.flush()  # make sure we have user.id
    session.refresh(user)
    if user.is_owner or user.is_admin:
        seed_rich_data(session, user.id)
    else:
        seed_demo_data(session, user.id)


# Minimal dataset for demo users
def seed_demo_data(session: Session, user_id: int) -> None:
    now = datetime.now(ZoneInfo("UTC"))

    # Create a couple tags for variety
    demo_tag = Tag(name="demo", user_id=user_id)
    health_tag = Tag(name="health", user_id=user_id)
    work_tag = Tag(name="work", user_id=user_id)

    # Tasks, show different statuses and priorities
    task1 = Task(
        name="Review job applications",
        priority=PriorityEnum.HIGH,
        is_done=False,
        user_id=user_id,
    )
    task1.tags.append(work_tag)

    task2 = Task(
        name="Update portfolio README",
        priority=PriorityEnum.MEDIUM,
        is_done=False,
        due_date=now + timedelta(days=3),
        user_id=user_id,
    )
    task2.tags.append(work_tag)

    task3 = Task(
        name="Morning workout", priority=PriorityEnum.LOW, is_done=True, user_id=user_id
    )
    task3.tags.append(health_tag)

    # Habits, with varying completion history
    habit1 = Habit(
        name="Daily coding practice",
        user_id=user_id,
        target_frequency=4,
    )
    habit1.tags.append(work_tag)

    habit2 = Habit(
        name="Exercise",
        user_id=user_id,
        target_frequency=4,
    )
    habit2.tags.append(health_tag)

    habit3 = Habit(
        name="Read documentation",
        user_id=user_id,
        target_frequency=4,
    )
    habit3.tags.append(demo_tag)

    for i in range(3):
        completion = HabitCompletion(
            habit=habit1, user_id=user_id, created_at=now - timedelta(days=i)
        )
        session.add(completion)

    # Time entries
    time1 = TimeEntry(
        category="Coding",
        description="Built new feature for task module",
        started_at=now - timedelta(hours=3),
        ended_at=now - timedelta(hours=1, minutes=30),
        duration_minutes=90,
        user_id=user_id,
    )

    time2 = TimeEntry(
        category="Learning",
        description="Studied deployment best practices",
        started_at=now - timedelta(days=1, hours=2),
        ended_at=now - timedelta(days=1, hours=1),
        duration_minutes=60,
        user_id=user_id,
    )

    time3 = TimeEntry(
        category="Exercise",
        description="Morning run",
        started_at=now - timedelta(hours=5),
        ended_at=now - timedelta(hours=4, minutes=30),
        duration_minutes=30,
        user_id=user_id,
    )

    # Metrics
    metric1 = DailyMetrics(
        entry_datetime=datetime(2025, 11, 23, tzinfo=ZoneInfo("UTC")),
        weight=70.5,
        steps=8500,
        calories=2100,
        wake_time=now.replace(hour=7, minute=0),
        sleep_time=(now - timedelta(days=1)).replace(hour=23, minute=30),
        user_id=user_id,
        created_at=now - timedelta(days=1),
    )

    metric2 = DailyMetrics(
        entry_datetime=datetime(2025, 11, 23, tzinfo=ZoneInfo("UTC")),
        weight=70.3,
        steps=10200,
        calories=2050,
        wake_time=now.replace(hour=6, minute=45),
        sleep_time=(now - timedelta(days=1)).replace(hour=23, minute=0),
        user_id=user_id,
        created_at=now,
    )

    # Add everything
    session.add_all(
        [
            demo_tag,
            health_tag,
            work_tag,
            task1,
            task2,
            task3,
            habit1,
            habit2,
            habit3,
            time1,
            time2,
            time3,
            metric1,
            metric2,
        ]
    )


# Comprehensive dataset for development
def seed_rich_data(session: Session, user_id: int) -> None:
    pass
