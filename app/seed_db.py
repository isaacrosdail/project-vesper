# Basic script to seed our db with dummy data for demo purposes

import random
from datetime import datetime, timedelta, timezone

from app.core.database import db_session
from app.modules.groceries.models import Product, Transaction
from app.modules.habits.models import Habit, HabitCompletion
from app.modules.tasks.models import Task


def seed_db():
    session = db_session()
    try:

        # Clear existing data
        session.query(Transaction).delete()
        session.query(Task).delete()
        session.query(Product).delete()
        session.query(Habit).delete()
        session.query(HabitCompletion).delete()

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

        # Add some sample habit completions
        habit_completions = [
            HabitCompletion(habit_id=1, completed_at=datetime.now(timezone.utc) - timedelta(days=1)),
            HabitCompletion(habit_id=1, completed_at=datetime.now(timezone.utc)),
            HabitCompletion(habit_id=2, completed_at=datetime.now(timezone.utc))
        ]

        session.add_all(tasks + habits + habit_completions)

        # Create & add products
        products = [
            Product(
                product_name="Huel Energy Drink",
                barcode="5060419750",
                net_weight=250.0
            ),
            Product(
                product_name="Organic Bananas",
                barcode="504350",
                net_weight=1000.0
            ),
            Product(
                product_name="Greek Yogurt",
                barcode="72736376",
                net_weight=500.0
            )
        ]

        session.add_all(products)
        session.flush() # Flush to get IDs for transactions

        # Create transactions
        transactions = []

        # For timezone-aware entries
        now_utc = datetime.now(timezone.utc)

        # Create 15 random transactions
        for i in range(10):
            random_product = random.choice(products)
            days_ago = random.randint(0, 30)

            # Create a transaction
            transactions.append(
                Transaction(
                    product_id=random_product.product_id,
                    price_at_scan=random.uniform(2.5, 10.0), # SQLAlchemy will automatically handle conversion from float to Numeric
                    quantity=random.randint(1, 5),
                    date_scanned= now_utc - timedelta(days=days_ago)
                )
            )

        session.add_all(transactions)
        session.commit()

        return "DB seeded successfully"

    finally:
        session.close()