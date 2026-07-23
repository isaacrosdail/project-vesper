"""
Helpers to seed data based on desired stats stuff.
Many are fed by .json files found in adjacent data dir.
"""
from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from app.shared.database.helpers import delete_user_activity_data

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from app.modules.groceries.models import (
    Product,
    ProductCategoryEnum,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    ShoppingListItem,
    Transaction,
    UnitEnum,
)
from app.modules.habits.models import Habit, HabitCompletion
from app.modules.metrics.models import DailyMetrics
from app.modules.tasks.models import PriorityEnum, Task
from app.modules.time_tracking.models import TimeEntry
from app.shared.fractional_indexing import generate_key_between
from app.shared.models import Pillar

SEED_DIR = Path(__file__).parent / "data"


class Tier(StrEnum):
    HIGH = auto()
    MED = auto()
    LOW = auto()

TIER_PARAMS = {
    Tier.HIGH: {"wake_hour": (6,8), "sleep_hour": (22,24), "steps": (8000, 12000), "calories": (2600, 2800)},
    Tier.MED: {"wake_hour": (7,8), "sleep_hour": (23,24), "steps": (4000, 6000), "calories": (2400, 2500)},
    Tier.LOW: {"wake_hour": (8,9), "sleep_hour": (23,24), "steps": (1000, 3000), "calories": (1900, 2200)},

}

class Level(StrEnum):
    BASIC = auto()
    MED = auto()
    RICH = auto()


LEVEL_PARAMS = {
    Level.BASIC: { "days": 14 },
    Level.MED: { "days": 30 },
    Level.RICH: { "days": 60 },
}

class Performance(StrEnum):
    STRONG = auto()
    AVERAGE = auto()
    WEAK = auto()

PERF_WEIGHTS: dict[Performance, dict[Tier, int]] = {
    Performance.STRONG:  {Tier.HIGH: 6, Tier.MED: 3, Tier.LOW: 1},
    Performance.AVERAGE: {Tier.HIGH: 3, Tier.MED: 4, Tier.LOW: 3},
    Performance.WEAK:    {Tier.HIGH: 1, Tier.MED: 3, Tier.LOW: 6},
}
def roll_tier(perf: Performance) -> Tier:
    weights = PERF_WEIGHTS[perf]
    return random.choices(list(weights), weights=list(weights.values()))[0]


def seed_pillars(session: Session, user_id: int) -> None:
    pillars = [
        Pillar(name="Health", user_id=user_id),
        Pillar(name="Career", user_id=user_id),
        Pillar(name="Purpose", user_id=user_id),
        Pillar(name="Rest", user_id=user_id),
        Pillar(name="Relationships", user_id=user_id),
    ]
    session.add_all(pillars)

# Orchestrator / Entrypoint
def seed_data(
    session: Session, user_id: int,
    level: Level = Level.BASIC,
    performance: Performance = Performance.AVERAGE
) -> int:
    delete_user_activity_data(session, user_id) # wipe data
    seed_pillars(session, user_id) # seed then fetch
    pillars = {
        p.name: p
        for p in session.scalars(select(Pillar).where(Pillar.user_id==user_id))
    }

    all_entries = seed_rich_data(pillars, user_id, level, performance)
    session.add_all(all_entries)
    session.flush()
    return len(all_entries)


def create_time_entries(day: datetime, tier: Tier, category_pillars: dict[str, list[Pillar]], user_id: int) -> list[TimeEntry]:
    N_TIME_ENTRIES = {Tier.HIGH: 3, Tier.MED: 2, Tier.LOW: 1}
    n_entries = N_TIME_ENTRIES[tier]
    categories = random.sample(list(category_pillars.keys()), n_entries)

    entries = []
    current_time = day.replace(hour=random.randint(6, 10), minute=0, second=0, microsecond=0)

    for category in categories:
        duration = random.randint(30, 90)
        ended_at = current_time + timedelta(minutes=duration)

        entry = TimeEntry(
            category=category,
            started_at=current_time,
            ended_at=ended_at,
            duration_minutes=duration,
            user_id=user_id
        )
        entry.pillars = category_pillars[category]
        entries.append(entry)

        # Gap before next entry
        current_time = ended_at + timedelta(minutes=random.randint(15, 60))
    return entries


def create_daily_metrics(day: datetime, tier: Tier, user_id: int) -> DailyMetrics:
    # TODO: Need to tweak the ranges here to be realistic
    wake_hour = random.randint(*TIER_PARAMS[tier]["wake_hour"])
    sleep_hour = random.randint(*TIER_PARAMS[tier]["sleep_hour"])

    wake_datetime = day.replace(
        hour=wake_hour % 24, minute=random.randint(0, 59), second=0, microsecond=0
    )
    # Anchor to midnight + timedelta so day wraps properly
    midnight = day.replace(hour=0, minute=0, second=0, microsecond=0)
    sleep_datetime = midnight - timedelta(hours=24 - sleep_hour)

    sleep_duration_minutes = int(
        (wake_datetime - sleep_datetime).total_seconds() // 60
    )

    return DailyMetrics(
        entry_datetime=day.replace(hour=12, minute=0, second=0, microsecond=0),
        weight=round(75 + random.uniform(-0.5, 0.5), 1),
        steps=random.randint(*TIER_PARAMS[tier]["steps"]),
        calories=random.randint(*TIER_PARAMS[tier]["calories"]),
        wake_datetime=wake_datetime,
        sleep_datetime=sleep_datetime,
        sleep_duration_minutes=sleep_duration_minutes,
        user_id=user_id,
    )


def create_habit_completions(day: datetime, tier: Tier, habits: list[Habit], user_id: int) -> list[HabitCompletion]:
    N_COMPLETIONS = {Tier.HIGH: (3,5), Tier.MED: (1,3), Tier.LOW: (0,2)}
    n = random.randint(*N_COMPLETIONS[tier])

    hour = random.randint(6, 22)
    created_at = day.replace(hour=hour, minute=0, second=0, microsecond=0)
    return [
        HabitCompletion(habit=h, created_at=created_at, completed_on=created_at.date(), user_id=user_id)
        for h in random.sample(habits, n)
    ]

# Comprehensive dataset for development
### TO be added: Recipes, Products, Transactions,
def seed_rich_data(pillars: Any, user_id: int, level: Level, performance: Performance) -> list[Any]:
    # ~30d data?
    # Roll score for "performance" - low/med/high
    # high = 3-4 completions, 90-180mins tracked
    # med  = 1-2 completions, 30-90mins
    # low  = 0-1 completions, 0-30mins
    #### TODO: ADD tags too!!
    # Accumulate, don't session.add!
    entries: list[Any] = []

    # HABITS
    with Path(f"{SEED_DIR}/habits.json").open() as f:
        habit_data = json.load(f)
    habits = []
    for h in habit_data:
        habit = Habit(name=h["name"], user_id=user_id, target_frequency=random.randint(1, 7))
        habit.pillars = [pillars[name] for name in h["pillars"]]
        habits.append(habit)
    entries.extend(habits)

    ### TASKS: name, is_done, is_frog OR priority (enum), due_date (mix: some needed for frogs, some optional for tasks)
    ## ~12-15 tasks total
    now = datetime.now(ZoneInfo("UTC"))
    with Path(f"{SEED_DIR}/tasks.json").open() as f: # better? modern/OS-agnostic path handling
        data = json.load(f)
    # Could also do:
    # data = json.loads(Path(f"{SEED_DIR}/tasks.json").read_text())
    tasks = create_tasks(data, now, user_id, pillars)

    entries.extend(tasks)

    with Path(f"{SEED_DIR}/time_categories.json").open() as f:
        category_data = json.load(f)
    category_pillars = {
        category: [pillars[name] for name in names]
        for category, names in category_data.items()
    }

    for day_offset in range(1, LEVEL_PARAMS[level]["days"]):
        day = datetime.now(ZoneInfo("UTC")) - timedelta(days=day_offset)

        tier = roll_tier(performance)

        entries.extend(create_habit_completions(day, tier, habits, user_id))
        entries.extend(create_time_entries(day, tier, category_pillars, user_id))
        entries.append(create_daily_metrics(day, tier, user_id))
    entries.extend(create_groceries(user_id, LEVEL_PARAMS[level]["days"]))

    return entries


def create_tasks(data: Any, now: datetime, user_id: int, pillars: dict[str, Pillar]) -> list[Task]:
    # Past 7 days - feeds overdue + frog stats
    tasks = []
    task_lookup = {}
    prev_key = None
    for t in data:
        sort_key = generate_key_between(prev_key, None)
        prev_key = sort_key

        task = (Task(
            name=t["name"],
            priority=PriorityEnum(t["priority"]),
            completed_at=now + timedelta(days=t["completed_at_offset"]) if t["completed_at_offset"] is not None else None,
            due_date=now + timedelta(days=t["due_date_offset"]) if t["due_date_offset"] is not None else None,
            user_id=user_id,
            created_at=now - timedelta(days=14),
            sort_key=sort_key
        ))
        task.pillars = [pillars[name] for name in t.get("pillars", [])]
        tasks.append(task)
        task_lookup[t["name"]] = task

    # Pass 2: Links for sub/supertasks
    for t in data:
        for subtask_name in t.get("subtasks", []):
            task_lookup[t["name"]].subtasks.append(task_lookup[subtask_name])
    return tasks


def create_groceries(user_id: int, days: int) -> list[Any]:
    now = datetime.now(ZoneInfo("UTC"))

    entries: list[Any] = []

    with Path(f"{SEED_DIR}/products.json").open() as f:
        data = json.load(f)

    p = {}
    for key, attrs in data.items():
        p[key] = Product(
            name=attrs["name"],
            category=ProductCategoryEnum(attrs["category"]),
            net_weight=attrs["net_weight"],
            unit_type=UnitEnum(attrs["unit_type"]),
            calories_per_100g=attrs["calories_per_100g"],
            user_id=user_id
        )
    entries.extend(p.values())

    # Shopping list
    with Path(f"{SEED_DIR}/shopping_list.json").open() as f:
        sl_data = json.load(f)
    shopping_list = ShoppingList(name=sl_data["name"], user_id=user_id)
    entries.append(shopping_list)

    entries.extend(
        ShoppingListItem(
            shopping_list=shopping_list,
            product=p[item["product"]],
            quantity_wanted=item["quantity"],
            user_id=user_id,
        )
        for item in sl_data["items"]
    )

    # Transactions: weighted pool of products, spread over the seeded window
    pool = [
        (key, attrs["base_price"])
        for key, attrs in data.items()
        for _ in range(attrs["frequency_weight"])
    ]
    for day_offset in range(0, days, 2):
        if random.random() < 0.3:
            continue
        day = now - timedelta(days=day_offset)

        for key, base_price in random.sample(pool, random.randint(1, 4)):
            entries.append(
                Transaction(
                    product=p[key],
                    price_at_scan=round(base_price * random.uniform(0.95, 1.05), 2),
                    quantity=1,
                    user_id=user_id,
                    created_at=day.replace(
                        hour=random.randint(8, 20), minute=random.randint(0, 59)
                    ),
                )
            )

    # Recipes
    with Path(f"{SEED_DIR}/recipes.json").open() as f:
        recipe_data = json.load(f)
    for r in recipe_data:
        recipe = Recipe(
            name=r["name"],
            yields=r["yields"],
            yields_units=UnitEnum(r["yields_units"]),
            user_id=user_id,
        )
        entries.append(recipe)
        entries.extend(
            RecipeIngredient(
                recipe=recipe,
                product=p[ing["product"]],
                amount_value=ing["amount"],
                amount_units=UnitEnum(ing["units"]),
                user_id=user_id,
            )
            for ing in r["ingredients"]
        )

    return entries
