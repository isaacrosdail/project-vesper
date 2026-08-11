import json
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import inspect

from app.modules.tasks.models import Task
from app.shared.database.seed.seed_db import (
    SEED_DIR,
    Tier,
    create_daily_metrics,
    create_tasks,
)
from app.shared.models import Pillar, Tag

tz_info = ZoneInfo("UTC")


# Half-open [low, high) in minutes; the ranges TIER_PARAMS can actually produce.
# Floors are strictly ordered, so a tier that sleeps better than the one above it
# fails here.
SLEEP_BOUNDS_MINUTES = {
    Tier.HIGH: (7 * 60, 10 * 60),
    Tier.MED: (6 * 60, 9 * 60),
    Tier.LOW: (5 * 60, 8 * 60),
}

def test_create_daily_metrics():
    day = datetime(2026, 5, 5, tzinfo=tz_info)
    user_id = 1

    for tier, (low, high) in SLEEP_BOUNDS_MINUTES.items():
        metrics = [create_daily_metrics(day, tier, user_id) for _ in range(50)]
        assert all(low <= m.sleep_duration_minutes < high for m in metrics), tier


def test_create_daily_metrics_carries_properly(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, _b: a) # force min roll
    day = datetime(2026, 5, 5, tzinfo=tz_info)

    metric = create_daily_metrics(day, Tier.MED, user_id=1)
    # midnight = day.replace(hour=0, minute=0, second=0, microsecond=0)
    # sleep_datetime = midnight - timedelta(hours=24 - sleep_hour)

    # MED's lowest sleep_hour is 24, which must anchor to midnight opening `day`
    # (5-5-2026), NOT 5-4-2026.
    assert metric.sleep_datetime == datetime(2026, 5, 5, tzinfo=tz_info)
    assert metric.sleep_duration_minutes == 7 * 60


def make_pillars(user_id: int) -> dict[str, Pillar]:
    return {
        "Health": Pillar(name="Health", user_id=user_id),
        "Rest": Pillar(name="Rest", user_id=user_id),
        "Relationships": Pillar(name="Relationships", user_id=user_id),
        "Purpose": Pillar(name="Purpose", user_id=user_id),
        "Career": Pillar(name="Career", user_id=user_id),
    }

def make_tags(data: list[dict], user_id: int) -> dict[str, Tag]:
    """Build exactly the tag vocabulary the given records reference."""
    names = sorted({name for record in data for name in record.get("tags", [])})
    return {name: Tag(name=name, user_id=user_id) for name in names}

def test_create_tasks():
    user_id = 1

    with Path(f"{SEED_DIR}/tasks.json").open() as f: # better? modern/OS-agnostic path handling
        data = json.load(f)

    FIXED_NOW = datetime(2026, 5, 5, tzinfo=ZoneInfo("UTC"))
    tasks = create_tasks(data, FIXED_NOW, user_id, make_pillars(user_id), make_tags(data, user_id))

    for i in range(len(tasks)):
        assert tasks[i]

ALLOWED_KEYS = {"name", "priority", "completed_at_offset", "due_date_offset", "pillars", "tags", "subtasks"}
def test_real_tasks_json_is_valid():
    user_id = 1
    data = json.loads(Path(f"{SEED_DIR}/tasks.json").read_text())

    for entry in data:
        assert set(entry) <= ALLOWED_KEYS, f"unknown keys in {entry.get('name')}: {set(entry) - ALLOWED_KEYS}"

    FIXED_NOW = datetime(2026, 5, 5, tzinfo=ZoneInfo("UTC"))
    tasks = create_tasks(
        data, FIXED_NOW, user_id=1, pillars=make_pillars(user_id), tags=make_tags(data, user_id)
    )
    assert len(tasks) == len(data)
    assert {t.name for task in tasks for t in task.tags} == set(make_tags(data, user_id))

SEED_HANDLED_COLS = {
    "id", "name", "priority", "completed_at", "due_date",
    "created_at", "updated_at", "sort_key", "user_id",
}

def test_new_task_columns_missing():
    actual = set(inspect(Task).columns.keys())
    assert actual == SEED_HANDLED_COLS, (
        f"Task cols changed: {actual ^ SEED_HANDLED_COLS}. "
    )
