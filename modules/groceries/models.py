# Handles DB setup/functionality & grocery related DB functions
from core.database import get_session, engine
from sqlalchemy.orm import declarative_base, relationship, joinedload
from sqlalchemy import ForeignKey
from datetime import date

# Making a model for Product (use base classes later but stick with this for now)
## Metadata needed to register the table properly? Investigate later
from sqlalchemy import Table, Column, Integer, String, DECIMAL, Float, Date

Base = declarative_base()

# Product Model to link products to barcodes, etc
class Product(Base):
	__tablename__ = "product"

	product_id = Column(Integer, primary_key=True)
	product_name = Column(String(100), nullable=False)
	barcode = Column(String(64), unique=True, nullable=False)
	price = Column(DECIMAL(10,2), nullable=False)
	net_weight = Column(Float, nullable=False)
	#quantity = Column(Integer, nullable=False)

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
	date_scanned = Column(Date)

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

# Eager load the 'product' relationship using joinedload
# so we can safely access transaction.product.* fields in templates
# after the session is closed (avoids DetachedInstanceError)
def get_all_transactions():
	session = get_session()
	transactions = session.query(Transaction).options(joinedload(Transaction.product)).all()
	session.close()
	return transactions

def handle_barcode(barcode, **product_data): # Uses **kwargs to take in optional data (ie., from forms)
	session = get_session()
	product = session.query(Product).filter_by(barcode=barcode).first()

	# If not in Product table, then add it
	if not product:
		product_name = product_data.get("product_name")
		price= product_data.get("price_at_scan")
		net_weight = product_data.get("net_weight")

		add_product(session, barcode, **product_data)
		product = session.query(Product).filter_by(barcode=barcode).first()
	# Then add product to our transaction table
	add_transaction(session, product, **product_data)

	session.commit()
	session.close()

# Handles new barcodes
def add_product(session, barcode, **product_data):
	#session = get_session()

	product_name = product_data.get("product_name")
	price_at_scan = product_data.get("price_at_scan")
	net_weight = product_data.get("net_weight")

	product = Product(barcode=barcode, product_name=product_name, price=price_at_scan, net_weight=net_weight)
	session.add(product)

	session.commit()
	session.close()

def add_transaction(session, product, **product_data):
	today = date.today()

	price_at_scan = product_data.get("price_at_scan")
	net_weight = product_data.get("net_weight")
	quantity = int(product_data.get("quantity") or 1)

	# session = get_session()
	# Check transaction table to see if we need to increment quantity for today's scans or add new instance of given product
	transaction = session.query(Transaction).filter_by(product_id=product.product_id, date_scanned=today).first()
	if transaction:
		transaction.quantity += quantity
	else:
		transaction = Transaction(product_id=product.product_id, price_at_scan=price_at_scan, quantity=quantity, date_scanned=today)
		session.add(transaction)

	session.commit()
	session.close()