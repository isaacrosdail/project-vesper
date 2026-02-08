# tests/test_api_serialization.py
from datetime import datetime, timezone

from app.modules.groceries.models import (
    Product,
    ProductCategoryEnum,
    UnitEnum,
)
from app.modules.habits.models import Habit, StatusEnum
from app.modules.metrics.models import DailyMetrics
from app.modules.tasks.models import PriorityEnum, Task
from app.modules.time_tracking.models import TimeEntry
from tests.fixtures import product_fixture


def test_product2_to_api_dict():
    product = Product(
        id=42,
        name="Red Widget",
        category=ProductCategoryEnum.FRUITS,
        barcode=123456789101213,
        net_weight=12.11,
        unit_type=UnitEnum.G,
        calories_per_100g=105,
        created_at=1,
        deleted_at=None,
    )

    result = product.to_api_dict()

    assert result == {
        "id": 42,
        "name": "Red Widget",
        "category": "FRUITS",
        "barcode": 123456789101213,
        "net_weight": 12.11,
        "unit_type": "G",
        "calories_per_100g": 105,
        "created_at": 1,
        "deleted_at": None,
        "subtype": "products",
    }


def test_product_to_api_dict():
    product = product_fixture(id=42)
    result = product.to_api_dict()

    assert result["id"] == 42
    assert result["name"] == "Test Apple"
    assert result["category"] == "FRUITS"
    assert result["barcode"] == "1234567890123"
    assert result["net_weight"] == 150.0
    assert result["unit_type"] == "G"
    assert result["calories_per_100g"] == 52
    assert result["deleted_at"] is None
    assert result["subtype"] == "products"


def test_task_roundtrip():
    """The most important test: does data survive the full cycle?"""
    # 1. Create a task
    task = Task(
        name="Test Task",
        priority=PriorityEnum.HIGH,
        is_done=False,
        due_date=datetime(2025, 10, 8, 14, 0, tzinfo=timezone.utc),
    )

    result = task.to_api_dict()

    assert result["name"] == "Test Task"
    assert result["priority"] == "HIGH"  # Enum converted to string
    assert (
        result["due_date"] == "2025-10-08T14:00:00+00:00"
    )  # Datetime converted to ISO
    assert result["subtype"] == "tasks"
    assert "user_id" not in result  # Excluded field


def test_task_serialization():
    task = Task(
        name="Test Task",
        priority=PriorityEnum.HIGH,
        is_done=False,
        due_date=datetime(2025, 10, 8, 14, 0, tzinfo=timezone.utc),
    )
    result = task.to_api_dict()

    assert result["name"] == "Test Task"
    assert result["priority"] == "HIGH"
    assert not result["is_done"]
    assert result["due_date"] == "2025-10-08T14:00:00+00:00"
    assert result["subtype"] == "tasks"
    assert "user_id" not in result


def test_habit_serialization():
    habit = Habit(
        name="Exercise", status=StatusEnum.EXPERIMENTAL, established_date=None
    )
    result = habit.to_api_dict()

    assert result["name"] == "Exercise"
    assert result["status"] == "EXPERIMENTAL"
    assert result["established_date"] is None
    assert result["subtype"] == "habits"
    assert "user_id" not in result
    assert "promotion_threshold" in result  # Model-specific exclusion


def test_daily_metrics_serialization():
    entry = DailyMetrics(
        weight=175.5,
        steps=8500,
        calories=2100,
        wake_datetime=datetime(2025, 10, 7, 14, 0, tzinfo=timezone.utc),
        sleep_datetime=datetime(2025, 10, 7, 3, 0, tzinfo=timezone.utc),
    )
    result = entry.to_api_dict()

    assert result["weight"] == 175.5
    assert result["steps"] == 8500
    assert result["calories"] == 2100
    assert result["wake_datetime"] == "2025-10-07T14:00:00+00:00"
    assert result["sleep_datetime"] == "2025-10-07T03:00:00+00:00"
    assert result["subtype"] == "daily_metrics"
    assert "user_id" not in result


def test_timeentry_serialization():
    entry = TimeEntry(
        category="work",
        duration_minutes=120,
        started_at=datetime(2025, 10, 7, 9, 0, tzinfo=timezone.utc),
        description="Testing",
    )
    result = entry.to_api_dict()

    assert result["category"] == "work"
    assert result["duration_minutes"] == 120
    assert result["started_at"] == "2025-10-07T09:00:00+00:00"
    assert result["subtype"] == "time_entries"
    assert "user_id" not in result
