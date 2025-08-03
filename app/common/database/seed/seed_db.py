# Basic script to seed our db with dummy data for demo purposes

import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError

from app.core.database import database_connection
from app.core.auth.models import User
from app.modules.groceries.models import Product, Transaction
from app.modules.habits.models import Habit, HabitCompletion
from app.modules.metrics.models import DailyIntention, DailyMetric
from app.modules.tasks.models import Task

from flask_login import current_user

# Minimal dataset for demo users
def seed_basic_data(user_id, session):
    pass

# Comprehensive dataset for development
def seed_rich_data(user_id, session):
    pass

def seed_db():

    with database_connection() as session:
        try:
            # Populate default user (separate transaction)
            default_user = User(id=1, username='default')
            session.add(default_user)
            session.flush() # flush to assign ID to user before referencing it below
        except IntegrityError:
            # session.rollback() # clear failed transaction
            print("User already exists, skipping..")

    with database_connection() as session:
        # Restore DailyIntention default text
        daily_intention = DailyIntention(intention="What's your focus today?")

        # Seed DailyMetric sample data for Plotly graphs
        # Weights for last X days
        LAST_X_DAYS = 14

        weight_metrics = [
            DailyMetric(created_at=datetime.now(timezone.utc) - timedelta(days=i),
                        metric_type="weight",
                        unit="lbs",
                        value=170 + random.uniform(-2, 2)) # uniform = float
            for i in range(LAST_X_DAYS)
        ]
        steps_metrics = [
            DailyMetric(created_at=datetime.now(timezone.utc) - timedelta(days=i),
                        metric_type="steps",
                        unit="steps",
                        value=6000 + random.randint(-2000, 3000)) # randint = int (obv)
            for i in range(LAST_X_DAYS)
        ]
        movement_metrics = [
            DailyMetric(created_at=datetime.now(timezone.utc) - timedelta(days=i),
                        metric_type="movement",
                        unit="minutes",
                        value=90 + random.uniform(-20, 20))
            for i in range(LAST_X_DAYS)
        ]

        # Create regular tasks (no more is_anchor field -> moving to new Habit model entirely)
        tasks = [
            # Regular Tasks
            Task(title="Buy groceries"),
            Task(title="Update portfolio website"),
            Task(title="Organize digital files")
        ]

        # Create habits in new Habit table
        habits = [
            Habit(title="AM Flashcards", category="learning", status="experimental"),
            Habit(title="30 Mins Project Work", category="work", status="experimental"),
            Habit(title="Walk Dog", category="household", status="established", 
                    established_date=datetime.now(timezone.utc))
        ]

        # Create & add products
        products = [
            Product(
                product_name="Huel Energy Drink",
                category="energy drink",
                barcode="94204197",
                net_weight=250.0,
                unit_type="ml",
                calories_per_100g=9
            ),
            Product(
                product_name="Organic Bananas",
                category="produce",
                barcode="50435087",
                net_weight=1000.0,
                unit_type="g",
                calories_per_100g=89
            ),
            Product(
                product_name="Greek Yogurt",
                category="diary",
                barcode="72736376",
                net_weight=500.0,
                unit_type="g",
                calories_per_100g=117
            )
        ]

        session.add(daily_intention)
        session.add_all(tasks + habits + products + weight_metrics + steps_metrics + movement_metrics)
        session.flush() # Flush to get product IDs for transactions

        # Add some sample habit completions
        # Note: Moved this below our flush, since HabitCompletions rely on Habits (Foreign key!!)
        #           Prior to our flush, Habits didn't even _have_ a foreign key, so that was fragile
        habit_completions = [
            HabitCompletion(habit_id=habits[0].id, created_at=datetime.now(timezone.utc) - timedelta(days=1)),
            HabitCompletion(habit_id=habits[0].id, created_at=datetime.now(timezone.utc)),
            HabitCompletion(habit_id=habits[1].id, created_at=datetime.now(timezone.utc))
        ]

        # Create 15 random transactions
        transactions = []
        now_utc = datetime.now(timezone.utc) # for timezone-aware entries

        for i in range(10):
            random_product = random.choice(products)
            days_ago = random.randint(0, 30)

            # Create a transaction
            transactions.append(
                Transaction(
                    product_id=random_product.id,
                    price_at_scan=random.uniform(2.5, 10.0), # SQLAlchemy will automatically handle conversion from float to Numeric
                    quantity=random.randint(1, 5),
                    created_at= now_utc - timedelta(days=days_ago)
                )
            )

        session.add_all(transactions + habit_completions)
        session.commit()

        return "DB seeded successfully"
    

    