# Handles DB setup/functionality & grocery related DB functions
from core.database import get_session, engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import ForeignKey

# Making a model for Product (use base classes later but stick with this for now)
## Metadata needed to register the table properly? Investigate later
from sqlalchemy import Table, Column, Integer, String, DECIMAL, Float

Base = declarative_base()

# Product Model to link products to barcodes, etc
class Product(Base):
	__tablename__ = "product"

	product_id = Column(Integer, primary_key=True)
	product_name = Column(String(100), nullable=False)
	barcode = Column(String(64), unique=True, nullable=False)
	price = Column(DECIMAL(10,2), nullable=False)
	net_weight = Column(Float, nullable=False)
	quantity = Column(Integer, nullable=False)

	# Human-readable column names
	COLUMN_LABELS = {
		"product_id": "Product ID",
		"product_name": "Product Name",
		"barcode": "Barcode",
		"price": "Price",
		"net_weight": "Net Weight (g)",
	}

# Transaction Model for logging what I bought
class Transaction(Base):
	__tablename__ = "transaction"

	transaction_id = Column(Integer, primary_key=True)
	product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)
	price_at_scan = Column(DECIMAL(10,2), nullable=False)
	quantity = Column(Integer, nullable=False)

	product = relationship("Product")

	# Human-readable column names
	COLUMN_LABELS = {
		"transaction_id": "Transaction #",
		"price_at_scan": "Price",
		"quantity": "Quantity",
	}

Base.metadata.create_all(engine) # Replaces our old Core style setup_schema function for database setup

# ORM style:
def get_all_products():
	session = get_session()
	products = session.query(Product).all()
	session.close()
	return products

def get_all_transactions():
	session = get_session()
	transactions = session.query(Transaction).all()
	session.close()
	return transactions

# Handles new barcodes
def add_product(barcode, name, price):
	session = get_session()
	
	# If product already exists, just inc the qty instead
	if new_product:
		new_product.quantity += 1
	else:
		new_product = Product(barcode=barcode, product_name=name, price=price, net_weight=20, quantity=1)
		session.add(new_product)
	session.commit()
	session.close()

def add_transaction(barcode):
	session = get_session()
	# Checks database for product to determine whether we need to add it as a new item
	product = session.query(Product).filter_by(barcode=barcode).first()
	# If it doesn't exist, also add it to the Products table
	if not product:
		add_product()