# Basic script to seed our db with dummy data for demo purposes
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.auth.models import User

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
from app.shared.models import Pillar, Tag

SEED_DIR = Path(__file__).parent

PRODUCTIVITY_HIGH = 0.7
PRODUCTIVITY_MED = 0.55

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
        completed_at=now,
        user_id=user_id,
    )
    task1.tags.append(work_tag)

    task2 = Task(
        name="Update portfolio README",
        priority=PriorityEnum.MEDIUM,
        completed_at=now,
        due_date=now + timedelta(days=3),
        user_id=user_id,
    )
    task2.tags.append(work_tag)

    task3 = Task(
        name="Morning workout", priority=PriorityEnum.LOW, completed_at=now, user_id=user_id
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
    session.add_all(
        [
            demo_tag, health_tag, work_tag,
            task1, task2, task3, habit1,
            habit2, habit3, time1, time2,
            time3, metric1, metric2,
        ]
    )


def create_time_entries(day: datetime, score: float, pillars: dict[str, Pillar], user_id: int) -> list[TimeEntry]:
    category_to_pillars = {
        "Programming": [pillars["Career"]],
        "Walk": [pillars["Health"]],
        "Tennis": [pillars["Health"], pillars["Relationships"]],
        "Mario party with friends": [pillars["Relationships"]],
        "Read": [pillars["Career"]],
        "Journaling": [pillars["Purpose"]],
        "Weightlifting": [pillars["Health"]],
        "Cooking": [pillars["Health"]],
        "Gaming": [pillars["Rest"]]
    }
    # weighted_categories = [
    #     ("Programming", 8),
    #     ("Walk", 5),
    #     ("Weightlifting", 4),
    #     ("Cooking", 3),
    #     ("Reading", 3),
    #     ("Journaling", 2),
    #     ("Tennis", 2),
    #     ("Mario party with friends", 1),
    #     ("Gaming", 1),
    # ]
    n_entries = 3 if score > PRODUCTIVITY_HIGH else 2 if score > PRODUCTIVITY_MED else 1
    categories = random.sample(list(category_to_pillars.keys()), n_entries)

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
        entry.pillars = category_to_pillars.get(category, [])
        entries.append(entry)

        # Gap before next entry
        current_time = ended_at + timedelta(minutes=random.randint(15, 60))
    return entries


def create_daily_metrics(day: datetime, score: float, user_id: int) -> DailyMetrics:
    # TODO: Need to tweak the ranges here to be realistic
    wake_hour  = random.randint(6, 8)   if score > PRODUCTIVITY_HIGH else random.randint(7, 9)
    sleep_hour = random.randint(22, 24) if score > PRODUCTIVITY_HIGH else random.randint(21, 24)

    wake_datetime = day.replace(
        hour=wake_hour % 24, minute=random.randint(0, 59), second=0, microsecond=0
    )
    sleep_datetime = (day - timedelta(days=1)).replace(
        hour=sleep_hour % 24, minute=random.randint(0, 59), second=0, microsecond=0
    )
    sleep_duration_minutes = int(
        (wake_datetime - sleep_datetime).total_seconds() // 60
    )

    steps = (
        random.randint(8000, 12000)
        if score > PRODUCTIVITY_HIGH
        else random.randint(3000, 8000)
        if score > PRODUCTIVITY_MED
        else random.randint(500, 3000)
    )

    return DailyMetrics(
        entry_datetime=day.replace(hour=12, minute=0, second=0, microsecond=0),
        weight=round(75 + random.uniform(-0.5, 0.5), 1),
        steps=steps,
        calories=random.randint(1800, 2600),
        wake_datetime=wake_datetime,
        sleep_datetime=sleep_datetime,
        sleep_duration_minutes=sleep_duration_minutes,
        user_id=user_id,
    )


def create_habit_completions(day: datetime, score: float, habits: list[Habit], user_id: int) -> list[HabitCompletion]:
    n = random.randint(3, 5) if score > PRODUCTIVITY_HIGH else random.randint(1, 3) if score > PRODUCTIVITY_MED else random.randint(0, 2)
    hour = random.randint(6, 22)
    created_at = day.replace(hour=hour, minute=0, second=0, microsecond=0)
    return [
        HabitCompletion(habit_id=h.id, created_at=created_at, user_id=user_id)
        for h in random.sample(habits, n)
    ]

# Comprehensive dataset for development
### TO be added: Recipes, Products, Transactions,
def seed_rich_data(session: Session, user_id: int) -> None:
    # ~30d data?
    # Roll score for "performance" - low/med/high
    # high = 3-4 completions, 90-180mins tracked
    # med  = 1-2 completions, 30-90mins
    # low  = 0-1 completions, 0-30mins

    # Grab Pillars
    pillars = {p.name: p for p in session.query(Pillar).filter_by(user_id=user_id).all()}

    # HABITS
    habit_names = ["Morning Walk", "30m Coding Drills", "Tidy workspace", "Journal 5mins", "Review weekly goals", "Jogging"]
    habits = [
        Habit(name=name, user_id=user_id, target_frequency=random.randint(1, 7))
        for name in habit_names
    ]
    habit_to_pillars = {
        "Morning Walk": [pillars["Health"]],
        "30m Coding Drills": [pillars["Career"]],
        "Tidy workspace": [],
        "Journal 5mins": [pillars["Purpose"]],
        "Review weekly goals": [pillars["Purpose"]],
        "Jogging": [pillars["Health"]]
    }
    for habit in habits:
        habit.pillars = habit_to_pillars.get(habit.name, [])
    session.add_all(habits)
    session.flush()

    ### TASKS: name, is_done, is_frog OR priority (enum), due_date (mix: some needed for frogs, some optional for tasks)
    ## ~12-15 tasks total
    now = datetime.now(ZoneInfo("UTC"))
    tasks = create_tasks(now, user_id, pillars)
    session.add_all(tasks)
    session.flush()

    for day_offset in range(1, 31):
        day = datetime.now(ZoneInfo("UTC")) - timedelta(days=day_offset)
        # Bias recent days (1-14) toward higher productivity, older days tend lower
        base_score = random.random()
        if day_offset <= 14:
            score = min(base_score + 0.3, 1.0) # crushing it recently
        elif day_offset <= 21:
            score = base_score
        else:
            score = max(base_score - 0.25, 1.0) # was slacking before
        # score = random.random()

        # HABIT COMPLETIONS
        session.add_all(create_habit_completions(day, score, habits, user_id))
        # TIME ENTRIES
        session.add_all(create_time_entries(day, score, pillars, user_id))
        # METRICS
        session.add(create_daily_metrics(day, score, user_id))

    seed_groceries(session, user_id)


def create_tasks(now: datetime, user_id: int, pillars: dict[str, Pillar]) -> list[Task]:
    # Past 7 days - feeds overdue + frog stats
    # with open(f"{SEED_DIR}/tasks.json") as f:
    with Path(f"{SEED_DIR}/tasks.json").open() as f: # better? modern/OS-agnostic path handling
        data = json.load(f)
    # Could also do:
    # data = json.loads(Path(f"{SEED_DIR}/tasks.json").read_text())

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


def seed_groceries(session: Session, user_id: int) -> None:
    now = datetime.now(ZoneInfo("UTC"))

    # with open(f"{SEED_DIR}/products.json") as f:
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
    session.add_all(p.values())
    session.flush()

    # Shopping list
    shopping_list = ShoppingList(name="Weekly Groceries", user_id=user_id)
    session.add(shopping_list)
    session.flush()

    session.add_all(
        [
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=p["milk"].id,
                quantity_wanted=1,
                user_id=user_id,
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=p["eggs"].id,
                quantity_wanted=2,
                user_id=user_id,
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=p["chicken"].id,
                quantity_wanted=2,
                user_id=user_id,
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=p["spinach"].id,
                quantity_wanted=1,
                user_id=user_id,
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=p["broccoli"].id,
                quantity_wanted=1,
                user_id=user_id,
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=p["yogurt"].id,
                quantity_wanted=3,
                user_id=user_id,
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=p["oats"].id,
                quantity_wanted=1,
                user_id=user_id,
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=p["almonds"].id,
                quantity_wanted=1,
                user_id=user_id,
            ),
        ]
    )
    # Transactions: weighted pool, spread over 60 days
    # (key, base_price, frequency_weight)
    catalog = [
        ("milk", 3.99, 8),
        ("eggs", 4.49, 7),
        ("chicken", 7.99, 6),
        ("spinach", 3.29, 5),
        ("broccoli", 1.99, 5),
        ("yogurt", 1.29, 5),
        ("banana", 0.49, 4),
        ("apple", 1.49, 4),
        ("ground_beef", 6.49, 3),
        ("carrot", 1.29, 3),
        ("bell_pepper", 1.69, 3),
        ("bread", 3.49, 3),
        ("rice", 2.99, 2),
        ("oats", 3.99, 2),
        ("cheese", 4.99, 2),
        ("black_beans", 1.09, 2),
        ("chickpeas", 1.09, 2),
        ("almonds", 7.99, 1),
        ("olive_oil", 10.99, 1),
        ("butter", 4.49, 1),
        ("soy_sauce", 3.49, 1),
        ("orange_juice", 4.99, 1),
    ]
    pool = [(k, price) for k, price, w in catalog for _ in range(w)]
    for day_offset in range(0, 60, 2):
        if random.random() < 0.3:
            continue
        day = now - timedelta(days=day_offset)

        for key, base_price in random.sample(pool, random.randint(1, 4)):
            session.add(
                Transaction(
                    product_id=p[key].id,
                    price_at_scan=round(base_price * random.uniform(0.95, 1.05), 2),
                    quantity=1,
                    user_id=user_id,
                    created_at=day.replace(
                        hour=random.randint(8, 20), minute=random.randint(0, 59)
                    ),
                )
            )

    # Recipes
    r_stir_fry = Recipe(
        name="Chicken Stir Fry", yields=4, yields_units=UnitEnum.EA, user_id=user_id
    )
    r_oatmeal = Recipe(
        name="Morning Oatmeal Bowl", yields=1, yields_units=UnitEnum.EA, user_id=user_id
    )
    r_eggs = Recipe(
        name="Scrambled Eggs", yields=1, yields_units=UnitEnum.EA, user_id=user_id
    )
    r_beef_bowl = Recipe(
        name="Beef Rice Bowl", yields=2, yields_units=UnitEnum.EA, user_id=user_id
    )
    r_salad = Recipe(
        name="Simple Spinach Salad", yields=1, yields_units=UnitEnum.EA, user_id=user_id
    )
    session.add_all([r_stir_fry, r_oatmeal, r_eggs, r_beef_bowl, r_salad])
    session.flush()

    recipe_ingredients = {
        r_stir_fry: [
            ("chicken", 500, "g"),
            ("broccoli", 200, "g"),
            ("bell_pepper", 150, "g"),
            ("soy_sauce", 30, "ml"),
            ("olive_oil", 20, "ml"),
            ("rice", 300, "g"),
        ],
        r_oatmeal: [
            ("oats", 80, "g"),
            ("banana", 1, "ea"),
            ("milk", 240, "ml"),
        ],
        r_eggs: [
            ("eggs", 3, "ea"),
            ("butter", 15, "g"),
            ("milk", 30, "ml"),
        ],
        r_beef_bowl: [
            ("ground_beef", 300, "g"),
            ("rice", 200, "g"),
            ("carrot", 100, "g"),
            ("soy_sauce", 20, "ml")
        ],
        r_salad: [
            ("spinach", 100, "g"),
            ("bell_pepper", 80, "g"),
            ("olive_oil", 15, "ml")
        ]
    }

    for recipe, ingredients in recipe_ingredients.items():
        for product_key, amount, units in ingredients:
            session.add(RecipeIngredient(
                recipe_id=recipe.id,
                product_id=p[product_key].id,
                amount_value=amount,
                amount_units=UnitEnum(units),
                user_id=user_id,
            ))
