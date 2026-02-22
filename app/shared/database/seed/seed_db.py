# Basic script to seed our db with dummy data for demo purposes
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.auth.models import User

import random
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
        wake_datetime=now.replace(hour=7, minute=0),
        sleep_datetime=(now - timedelta(days=1)).replace(hour=23, minute=30),
        user_id=user_id,
        created_at=now - timedelta(days=1),
    )

    metric2 = DailyMetrics(
        entry_datetime=datetime(2025, 11, 23, tzinfo=ZoneInfo("UTC")),
        weight=70.3,
        steps=10200,
        calories=2050,
        wake_datetime=now.replace(hour=6, minute=45),
        sleep_datetime=(now - timedelta(days=1)).replace(hour=23, minute=0),
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
### TO be added: Recipes, Products, Transactions, 
def seed_rich_data(session: Session, user_id: int) -> None:
    # ~30d data?
    # Roll score for "performance" - low/med/high
    # high = 3-4 completions, 90-180mins tracked
    # med  = 1-2 completions, 30-90mins
    # low  = 0-1 completions, 0-30mins
    # Create habits
    habit_names = ["walk", "eat", "talk", "sleep", "think", "move", "drink"]
    # Fields needed: name, target_frequency
    habits = [
        Habit(name=name, user_id=user_id, target_frequency=random.randint(1, 7))
        for name in habit_names
    ]
    session.add_all(habits)
    session.flush()

    time_entries_categories = ["Programming", "Walk", "Baseball huh?", "Social", "Read"]

    ### TASKS: name, is_done, is_frog OR priority (enum), due_date (mix: some needed for frogs, some optional for tasks)
    ## ~12-15 tasks total
    now = datetime.now(ZoneInfo("UTC"))
    tasks = create_tasks(now, user_id)
    session.add_all(tasks)

    for day_offset in range(1, 31):
        day = datetime.now(ZoneInfo("UTC")) - timedelta(days=day_offset)
        hour = random.randint(6, 22)
        score = random.random()

        if score > 0.7:  # high productivity
            n_completions = random.randint(3, 5)
            duration_minutes = random.randint(90, 180)
        elif score > 0.55:  # med productivity
            n_completions = random.randint(1, 3)
            duration_minutes = random.randint(30, 90)
        else:  # low productivity
            n_completions = random.randint(0, 2)
            duration_minutes = random.randint(0, 30)

        habits_done = random.sample(habits, n_completions)

        created_at = day.replace(hour=hour, minute=0, second=0, microsecond=0)

        for habit in habits_done:
            completion = HabitCompletion(
                habit_id=habit.id, created_at=created_at, user_id=user_id
            )
            session.add(completion)

        if duration_minutes != 0:
            ended_at = created_at + timedelta(minutes=duration_minutes)
            category = random.choice(time_entries_categories)
            time_entry = TimeEntry(
                category=category,
                started_at=created_at,
                ended_at=ended_at,
                duration_minutes=duration_minutes,
                user_id=user_id,
            )
            session.add(time_entry)

        ## METRICS:
        wake_hour = random.randint(6, 8) if score > 0.7 else random.randint(7, 9)
        sleep_hour = random.randint(22, 24) if score > 0.7 else random.randint(21, 24)

        wake_datetime = day.replace(hour=wake_hour % 24, minute=random.randint(0,
        59), second=0, microsecond=0)
        sleep_datetime = (day - timedelta(days=1)).replace(hour=sleep_hour % 24,
        minute=random.randint(0, 59), second=0, microsecond=0)
        sleep_duration_minutes = int((wake_datetime -
        sleep_datetime).total_seconds() // 60)

        steps = (
            random.randint(8000, 12000)
            if score > 0.7
            else random.randint(3000, 8000) if score > 0.55 else random.randint(500, 3000)
        )

        metric = DailyMetrics(
            entry_datetime=day.replace(hour=12, minute=0, second=0, microsecond=0),
            weight=round(75 + random.uniform(-0.5, 0.5), 1),
            steps=steps,
            calories=random.randint(1800, 2600),
            wake_datetime=wake_datetime,
            sleep_datetime=sleep_datetime,
            sleep_duration_minutes=sleep_duration_minutes,
            user_id=user_id,
        )
        session.add(metric)


def create_tasks(now: datetime, user_id: int) -> list[Task]:
    # Past 7 days — feeds overdue + frog stats
    tasks = [
        Task(
            name="Fix login bug",
            priority=PriorityEnum.HIGH,
            is_frog=False,
            is_done=False,
            due_date=now - timedelta(days=2),
            user_id=user_id,
        ),
        Task(
            name="Write tests",
            priority=PriorityEnum.MEDIUM,
            is_frog=False,
            is_done=True,
            due_date=now - timedelta(days=4),
            user_id=user_id,
        ),
        Task(
            name="Update resume",
            priority=PriorityEnum.LOW,
            is_frog=False,
            is_done=False,
            due_date=now - timedelta(days=1),
            user_id=user_id,
        ),
        # Frogs in window
        Task(
            name="Deploy to prod",
            is_frog=True,
            priority=None,
            is_done=True,
            due_date=now - timedelta(days=3),
            user_id=user_id,
        ),
        Task(
            name="Client call prep",
            is_frog=True,
            priority=None,
            is_done=False,
            due_date=now - timedelta(days=5),
            user_id=user_id,
        ),
        # Upcoming
        Task(
            name="Code review",
            priority=PriorityEnum.MEDIUM,
            is_frog=False,
            is_done=False,
            due_date=now + timedelta(days=2),
            user_id=user_id,
        ),
        Task(
            name="Weekly review",
            is_frog=True,
            priority=None,
            is_done=False,
            due_date=now + timedelta(days=1),
            user_id=user_id,
        ),
        # Undated backlog
        Task(
            name="Refactor auth module",
            priority=PriorityEnum.LOW,
            is_frog=False,
            is_done=False,
            user_id=user_id,
        ),
        Task(
            name="Read SICP",
            priority=PriorityEnum.LOW,
            is_frog=False,
            is_done=False,
            user_id=user_id,
        ),
    ]
    return tasks