# Handles DB setup/functionality & grocery related DB functions
from core.database import get_session, engine
from sqlalchemy.orm import declarative_base

# Making a model for Product (use base classes later but stick with this for now)
## Metadata needed to register the table properly? Investigate later
from sqlalchemy import Table, Column, Integer, String, DECIMAL, Float

Base = declarative_base()

class Product(Base):
	__tablename__ = "product"

	product_id = Column(Integer, primary_key=True)
	product_name = Column(String(100), nullable=False)
	price = Column(DECIMAL(10,2), nullable=False)
	net_weight = Column(Float, nullable=False)
	quantity = Column(Integer, nullable=False)

	# Human-readable column names
	COLUMN_LABELS = {
		"product_id": "Product ID",
		"product_name": "Product Name",
		"price": "Price",
		"net_weight": "Net Weight (g)",
		"quantity": "Quantity",
	}

Base.metadata.create_all(engine) # Replaces our old Core style setup_schema function for database setup

# ORM style:
def get_all_products():
	session = get_session()
	products = session.query(Product).all()
	session.close()
	return products

def add_product(barcode):
	session = get_session()
	# Checks database for product in case it already exists
	new_product = session.query(Product).filter_by(product_id=barcode).first()
	# If product already exists, just inc the qty instead
	if new_product:
		new_product.quantity += 1
	else:
		new_product = Product(product_id=barcode, product_name="Jam", price=1.29, net_weight=20, quantity=1)
		session.add(new_product)
	session.commit()
	session.close()