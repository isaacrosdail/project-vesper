# Basic script to seed our db with dummy data for dev & demo purposes

from app.core.database import db_session
from app.modules.groceries.models import Product, Transaction
from app.modules.tasks.models import Task
from datetime import datetime, timezone, timedelta
import random

def seed_db():
    session = db_session()
    try:

        # Clear existing data
        session.query(Transaction).delete()
        session.query(Task).delete()
        session.query(Product).delete()

        # Create & add tasks
        tasks = [
            # Anchor habit #1
            Task(
                title="AM Flashcards",
                type="habit",
                is_anchor=True,
            ),
            # Anchor habit #2
            Task(
                title="30 Mins Project Work",
                type="habit",
                is_anchor=True,
            ),
            # Anchor habit #3
            Task(
                title="Walk Puppers",
                type="habit",
                is_anchor=True,
            ),
            # Regular Tasks
            Task(title="Buy groceries"),
            Task(title="Update portfolio website"),
            Task(title="Organize digital files")
        ]

        session.add_all(tasks)

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

        return "DB seeded successfully with 6 Tasks (3 anchor habits, 3 todos), 3 Products, and 10 randomized Transactions for said Products"

    finally:
        session.close()