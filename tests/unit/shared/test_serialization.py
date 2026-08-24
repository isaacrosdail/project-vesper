# tests/test_api_serialization.py
import json
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.groceries.models import (
    Product,
    ProductCategoryEnum,
    Recipe,
    RecipeIngredient,
    ShoppingListItem,
    Transaction,
    UnitEnum,
)
from app.modules.groceries.schemas import (
    ProductRead,
    RecipeRead,
    ShoppingListItemRead,
    TransactionRead,
)
from app.modules.habits.models import Habit, HabitCompletion
from app.modules.habits.schemas import HabitCompletionRead, HabitRead
from app.modules.metrics.schemas import DailyMetricsCreate
from app.modules.tasks.models import PriorityEnum, Task
from app.modules.tasks.schemas import TaskCreate, TaskRead
from app.shared.models import Pillar
from app.shared.target import Target


def test_task_read_dump():
    task = Task(
        id=42,
        name="Test Task",
        priority=PriorityEnum.FROG,
        due_datetime=datetime(2025, 10, 8, 14, 0, tzinfo=timezone.utc),
        completed_at=datetime(2025, 10, 8, 15, 0, tzinfo=timezone.utc),
        sort_key="a0",
        created_at=datetime(2025, 10, 1, 9, 0, tzinfo=timezone.utc),
    )
    task.pillars.append(Pillar(id=1, name="Health"))
    task.subtasks.append(Task(id=43, name="Subtask1", priority=PriorityEnum.LOW, sort_key="a1"))

    assert TaskRead.dump(task) == {
        "id": 42,
        "name": "Test Task",
        "priority": "frog",
        "due_datetime": "2025-10-08T14:00:00Z",
        "completed_at": "2025-10-08T15:00:00Z",
        "sort_key": "a0",
        "created_at": "2025-10-01T09:00:00Z",
        "is_done": True,
        "subtasks": [43],
        "supertasks": [],
        "pillars": [{"id": 1, "name": "Health"}],
        "subtype": "tasks",
    }

def test_task_create_frog_requires_due_datetime():
    with pytest.raises(ValidationError):
        TaskCreate(name="x", priority=PriorityEnum.FROG)

def test_task_create_frog_with_due_datetime_ok():
    TaskCreate(name="x", priority=PriorityEnum.FROG, due_datetime="2025-10-08T14:00:00Z")


def test_habit_read_dump():
    habit = Habit(
        id=7,
        name="Exercise",
        established_date=datetime(2025, 9, 1, tzinfo=timezone.utc),
        weekly_frequency=3,
        created_at=datetime(2025, 8, 1, 9, 0, tzinfo=timezone.utc),
    )
    habit.pillars.append(Pillar(id=1, name="Health"))

    assert HabitRead.dump(habit) == {
        "id": 7,
        "name": "Exercise",
        "status": "experimental",
        "established_date": "2025-09-01T00:00:00Z",
        "weekly_frequency": 3,
        "created_at": "2025-08-01T09:00:00Z",
        "is_promotable": True,
        "pillars": [{"id": 1, "name": "Health"}],
        "subtype": "habits",
    }


def test_habit_completion_read_dump():
    completion = HabitCompletion(
        id=3,
        habit_id=7,
        completed_at=datetime(2025, 10, 8, 7, 30, tzinfo=timezone.utc),
        created_at=datetime(2025, 10, 8, 7, 30, tzinfo=timezone.utc),
    )
    assert HabitCompletionRead.dump(completion) == {
        "id": 3,
        "habit_id": 7,
        "completed_at": "2025-10-08T07:30:00Z",
        "created_at": "2025-10-08T07:30:00Z",
        "subtype": "habit_completions",
    }


def test_product_read_dump():
    product = Product(
        id=42,
        name="Oats",
        category=ProductCategoryEnum.GRAINS,
        barcode="1234567890123",
        net_weight=Decimal("0.125"),     # 3 decimals on purpose — pins full precision
        unit_type=UnitEnum.KG,
        calories_per_100g=370.0,
        protein_per_100g=13.0,
        fat_per_100g=7.0,
        carbs_per_100g=58.0,
        fat_mono_per_100g=2.0,
        fat_poly_per_100g=2.5,
        fat_sat_per_100g=1.2,
        carbs_fiber_per_100g=10.0,
        carbs_sugar_per_100g=1.0,
        sodium_per_100g=0.002,
        potassium_per_100g=0.43,
        deleted_at=None,
        created_at=datetime(2025, 8, 1, tzinfo=timezone.utc),
    )
    result = ProductRead.dump(product)
    assert result["net_weight"] == 0.125          # not 0.13
    assert "deleted_at" not in result             # intentional omission
    assert result == {
        "id": 42,
        "name": "Oats",
        "category": "grains",
        "barcode": "1234567890123",
        "net_weight": 0.125,
        "unit_type": "kg",
        "calories_per_100g": 370.0,
        "protein_per_100g": 13.0,
        "fat_per_100g": 7.0,
        "carbs_per_100g": 58.0,
        "fat_mono_per_100g": 2.0,
        "fat_poly_per_100g": 2.5,
        "fat_sat_per_100g": 1.2,
        "carbs_fiber_per_100g": 10.0,
        "carbs_sugar_per_100g": 1.0,
        "sodium_per_100g": 0.002,
        "potassium_per_100g": 0.43,
        "created_at": "2025-08-01T00:00:00Z",
        "subtype": "products"
    }


def test_transaction_read_dump():
    txn = Transaction(
        id=9,
        product_id=42,
        shopping_trip_id=None,
        price_at_scan=Decimal("3.50"),
        quantity=2,
        created_at=datetime(2025, 10, 8, tzinfo=timezone.utc),
    )
    txn.product = Product(id=42, name="Oats", net_weight=Decimal(500), unit_type=UnitEnum.G)

    result = TransactionRead.dump(txn)
    assert result["product_name"] == "Oats"
    assert result["net_weight"] == 500.0
    assert result["unit_type"] == "g"
    assert result["price_per_100g"] == 0.7        # 3.50 / 500 * 100
    assert result == {
        "created_at": "2025-10-08T00:00:00Z",
        "id": 9,
        "net_weight": 500.0,
        "price_at_scan": 3.5,
        "price_per_100g": 0.7,
        "product_id": 42,
        "product_name": "Oats",
        "quantity": 2,
        "shopping_trip_id": None,
        "unit_type": "g",
        "subtype": "transactions",
    }


def test_shopping_list_item_read_dump():
    item = ShoppingListItem(
        id=5,
        shopping_list_id=1,
        product_id=42,
        quantity_wanted=2,
        is_checked=True,
        created_at=datetime(2025, 10, 8, tzinfo=timezone.utc),
    )
    item.product = Product(id=42, name="Oats", net_weight=Decimal(500), unit_type=UnitEnum.G)
    assert ShoppingListItemRead.dump(item) == {
        "created_at": "2025-10-08T00:00:00Z",
        "id": 5,
        "is_checked": True,
        "net_weight": 500.0,
        "product_id": 42,
        "product_name": "Oats",
        "quantity_wanted": 2,
        "shopping_list_id": 1,
        "subtype": "shopping_list_items",
        "unit_type": "g"
    }


def test_recipe_read_dump():
    recipe = Recipe(
        id=2,
        name="Overnight Oats",
        yields=Decimal("2.5"),
        yields_units=UnitEnum.G,
        created_at=datetime(2025, 10, 8, tzinfo=timezone.utc),
    )
    ing = RecipeIngredient(product_id=42, amount_value=Decimal("0.125"),
amount_units=UnitEnum.KG)
    ing.product = Product(id=42, name="Oats")
    recipe.ingredients.append(ing)

    assert RecipeRead.dump(recipe) == {
        "id": 2,
        "name": "Overnight Oats",
        "yields": 2.5,
        "yields_units": "g",
        "ingredients": [
            {"product_id": 42, "product_name": "Oats", "amount_value": 0.125, "amount_units": "kg"}
        ],
        "created_at": "2025-10-08T00:00:00Z",
        "subtype": "recipes",
    }



def metrics_payload(**overrides: dict[str, float | int | str]) -> dict:
    return {
        "entry_date": "2026-07-09",
        "steps": 8000,
        "calories": 2100,
        "weight": 81.5,
        "weight_units": "kg",
    } | overrides

def test_at_least_one_metric_required():
    with pytest.raises(ValidationError):
        DailyMetricsCreate(entry_date="2026-07-09")
