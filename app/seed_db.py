# Basic script to seed our db with dummy data for the sake of development & showcasing for my portfolio

from app import db_session
from app.modules.groceries import models as grocery_models

def seed_data():
    if not db_session.query(grocery_models.Product).first():
        product = grocery_models.Product(product_name="Sample Product", barcode="666666", price=9.99, net_weight=300)
        db_session.add(product)
        db_session.commit()