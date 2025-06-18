# Basic script to seed our db with dummy data for demo purposes

import random
from datetime import datetime, timedelta, timezone

from app.core.database import db_session
from app.modules.groceries.models import Product, Transaction
from app.modules.habits.models import Habit, HabitCompletion, DailyIntention
from app.modules.tasks.models import Task


def seed_db():
    session = db_session()
    try:

        # Clear existing data
        # to study: cascade settings for tables
        session.query(Transaction).delete()
        session.query(Task).delete()
        session.query(Product).delete()
        session.query(HabitCompletion).delete()
        session.query(Habit).delete()
        session.query(DailyIntention).delete()

        # Restore DailyIntention default text
        dailyIntention = DailyIntention(intention="What's your focus today?")

        # Create regular tasks (no more is_anchor field -> moving to new Habit model entirely)
        tasks = [
            # Regular Tasks
            Task(title="Buy groceries"),
            Task(title="Update portfolio website"),
            Task(title="Organize digital files")
        ]

        # Create habits in new Habit table
        habits = [
            Habit(title="AM Flashcards", status="experimental"),
            Habit(title="30 Mins Project Work", status="experimental"),
            Habit(title="Walk Dog", status="established", 
                    established_date=datetime.now(timezone.utc))
        ]

        # Create & add products
        products = [
            Product(
                product_name="Huel Energy Drink",
                category="energy drink",
                barcode="5060419750",
                net_weight=250.0,
                unit_type="ml",
                calories_per_100g=9
            ),
            Product(
                product_name="Organic Bananas",
                category="produce",
                barcode="504350",
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

        session.add(dailyIntention)
        session.add_all(tasks + habits + products)
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

    finally:
        session.close()