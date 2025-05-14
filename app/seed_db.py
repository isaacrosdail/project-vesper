# Basic script to seed our db with dummy data for the sake of development & showcasing for my portfolio

from app.core.database import db_session
from app.modules.groceries import models as grocery_models

def seed_db():
    session = db_session()
    try: 
        if not session.query(grocery_models.Product).first():
            product = grocery_models.Product(
                product_name="Sample Product22",
                barcode="666666", 
                price=9.99, 
                net_weight=300
            )

            session.add(product)
            session.commit()
    finally:
        session.close()