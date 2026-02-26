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

from app.modules.groceries.models import (
    Product,
    ProductCategoryEnum,
    UnitEnum,
    Transaction,
    ShoppingList,
    ShoppingListItem,
    Recipe,
    RecipeIngredient,
)


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
        # TODO: Need to tweak the ranges here to be realistic
        wake_hour = random.randint(6, 8) if score > 0.7 else random.randint(7, 9)
        sleep_hour = random.randint(22, 24) if score > 0.7 else random.randint(21, 24)

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
            if score > 0.7
            else random.randint(3000, 8000)
            if score > 0.55
            else random.randint(500, 3000)
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

    seed_groceries(session, user_id)


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


def seed_groceries(session: Session, user_id: int) -> None:
    now = datetime.now(ZoneInfo("UTC"))

    p = {
        "banana": Product(
            name="Banana",
            category=ProductCategoryEnum.FRUITS,
            net_weight=120,
            unit_type=UnitEnum.EA,
            calories_per_100g=89,
            user_id=user_id,
        ),
        "apple": Product(
            name="Apple (Gala)",
            category=ProductCategoryEnum.FRUITS,
            net_weight=182,
            unit_type=UnitEnum.EA,
            calories_per_100g=52,
            user_id=user_id,
        ),
        "broccoli": Product(
            name="Broccoli",
            category=ProductCategoryEnum.VEGETABLES,
            net_weight=350,
            unit_type=UnitEnum.G,
            calories_per_100g=34,
            user_id=user_id,
        ),
        "spinach": Product(
            name="Baby Spinach",
            category=ProductCategoryEnum.VEGETABLES,
            net_weight=142,
            unit_type=UnitEnum.G,
            calories_per_100g=23,
            user_id=user_id,
        ),
        "bell_pepper": Product(
            name="Bell Pepper (Red)",
            category=ProductCategoryEnum.VEGETABLES,
            net_weight=164,
            unit_type=UnitEnum.EA,
            calories_per_100g=31,
            user_id=user_id,
        ),
        "carrot": Product(
            name="Carrots (bag)",
            category=ProductCategoryEnum.VEGETABLES,
            net_weight=453,
            unit_type=UnitEnum.G,
            calories_per_100g=41,
            user_id=user_id,
        ),
        "rice": Product(
            name="White Rice",
            category=ProductCategoryEnum.GRAINS,
            net_weight=907,
            unit_type=UnitEnum.G,
            calories_per_100g=365,
            user_id=user_id,
        ),
        "oats": Product(
            name="Rolled Oats",
            category=ProductCategoryEnum.GRAINS,
            net_weight=453,
            unit_type=UnitEnum.G,
            calories_per_100g=389,
            user_id=user_id,
        ),
        "bread": Product(
            name="Whole Wheat Bread",
            category=ProductCategoryEnum.BAKERY,
            net_weight=570,
            unit_type=UnitEnum.G,
            calories_per_100g=247,
            user_id=user_id,
        ),
        "milk": Product(
            name="Whole Milk (1 gal)",
            category=ProductCategoryEnum.DAIRY_EGGS,
            net_weight=3785,
            unit_type=UnitEnum.ML,
            calories_per_100g=61,
            user_id=user_id,
        ),
        "yogurt": Product(
            name="Greek Yogurt (plain)",
            category=ProductCategoryEnum.DAIRY_EGGS,
            net_weight=150,
            unit_type=UnitEnum.G,
            calories_per_100g=59,
            user_id=user_id,
        ),
        "eggs": Product(
            name="Eggs (12ct)",
            category=ProductCategoryEnum.DAIRY_EGGS,
            net_weight=12,
            unit_type=UnitEnum.EA,
            calories_per_100g=155,
            user_id=user_id,
        ),
        "cheese": Product(
            name="Cheddar Cheese",
            category=ProductCategoryEnum.DAIRY_EGGS,
            net_weight=226,
            unit_type=UnitEnum.G,
            calories_per_100g=402,
            user_id=user_id,
        ),
        "chicken": Product(
            name="Chicken Breast",
            category=ProductCategoryEnum.MEATS,
            net_weight=680,
            unit_type=UnitEnum.G,
            calories_per_100g=165,
            user_id=user_id,
        ),
        "ground_beef": Product(
            name="Ground Beef (80/20)",
            category=ProductCategoryEnum.MEATS,
            net_weight=454,
            unit_type=UnitEnum.G,
            calories_per_100g=254,
            user_id=user_id,
        ),
        "olive_oil": Product(
            name="Olive Oil",
            category=ProductCategoryEnum.FATS_OILS,
            net_weight=473,
            unit_type=UnitEnum.ML,
            calories_per_100g=884,
            user_id=user_id,
        ),
        "butter": Product(
            name="Unsalted Butter",
            category=ProductCategoryEnum.FATS_OILS,
            net_weight=454,
            unit_type=UnitEnum.G,
            calories_per_100g=717,
            user_id=user_id,
        ),
        "black_beans": Product(
            name="Black Beans (can)",
            category=ProductCategoryEnum.LEGUMES,
            net_weight=425,
            unit_type=UnitEnum.G,
            calories_per_100g=91,
            user_id=user_id,
        ),
        "chickpeas": Product(
            name="Chickpeas (can)",
            category=ProductCategoryEnum.LEGUMES,
            net_weight=400,
            unit_type=UnitEnum.G,
            calories_per_100g=164,
            user_id=user_id,
        ),
        "soy_sauce": Product(
            name="Soy Sauce",
            category=ProductCategoryEnum.CONDIMENTS_SAUCES,
            net_weight=300,
            unit_type=UnitEnum.ML,
            calories_per_100g=60,
            user_id=user_id,
        ),
        "almonds": Product(
            name="Almonds (raw)",
            category=ProductCategoryEnum.SNACKS,
            net_weight=170,
            unit_type=UnitEnum.G,
            calories_per_100g=579,
            user_id=user_id,
        ),
        "orange_juice": Product(
            name="Orange Juice",
            category=ProductCategoryEnum.BEVERAGES,
            net_weight=1890,
            unit_type=UnitEnum.ML,
            calories_per_100g=45,
            user_id=user_id,
        ),
    }
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

    session.add_all(
        [
            # Chicken Stir Fry
            RecipeIngredient(
                recipe_id=r_stir_fry.id,
                product_id=p["chicken"].id,
                amount_value=500,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_stir_fry.id,
                product_id=p["broccoli"].id,
                amount_value=200,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_stir_fry.id,
                product_id=p["bell_pepper"].id,
                amount_value=150,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_stir_fry.id,
                product_id=p["soy_sauce"].id,
                amount_value=30,
                amount_units=UnitEnum.ML,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_stir_fry.id,
                product_id=p["olive_oil"].id,
                amount_value=20,
                amount_units=UnitEnum.ML,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_stir_fry.id,
                product_id=p["rice"].id,
                amount_value=300,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            # Morning Oatmeal
            RecipeIngredient(
                recipe_id=r_oatmeal.id,
                product_id=p["oats"].id,
                amount_value=80,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_oatmeal.id,
                product_id=p["banana"].id,
                amount_value=1,
                amount_units=UnitEnum.EA,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_oatmeal.id,
                product_id=p["milk"].id,
                amount_value=240,
                amount_units=UnitEnum.ML,
                user_id=user_id,
            ),
            # Scrambled Eggs
            RecipeIngredient(
                recipe_id=r_eggs.id,
                product_id=p["eggs"].id,
                amount_value=3,
                amount_units=UnitEnum.EA,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_eggs.id,
                product_id=p["butter"].id,
                amount_value=15,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_eggs.id,
                product_id=p["milk"].id,
                amount_value=30,
                amount_units=UnitEnum.ML,
                user_id=user_id,
            ),
            # Beef Rice Bowl
            RecipeIngredient(
                recipe_id=r_beef_bowl.id,
                product_id=p["ground_beef"].id,
                amount_value=300,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_beef_bowl.id,
                product_id=p["rice"].id,
                amount_value=200,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_beef_bowl.id,
                product_id=p["carrot"].id,
                amount_value=100,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_beef_bowl.id,
                product_id=p["soy_sauce"].id,
                amount_value=20,
                amount_units=UnitEnum.ML,
                user_id=user_id,
            ),
            # Spinach Salad
            RecipeIngredient(
                recipe_id=r_salad.id,
                product_id=p["spinach"].id,
                amount_value=100,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_salad.id,
                product_id=p["bell_pepper"].id,
                amount_value=80,
                amount_units=UnitEnum.G,
                user_id=user_id,
            ),
            RecipeIngredient(
                recipe_id=r_salad.id,
                product_id=p["olive_oil"].id,
                amount_value=15,
                amount_units=UnitEnum.ML,
                user_id=user_id,
            ),
        ]
    )
