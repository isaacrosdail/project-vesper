# Handles DB setup/functionality & grocery related DB functions
from core.database import get_session, engine
from sqlalchemy.orm import declarative_base, relationship, joinedload
from sqlalchemy import ForeignKey
from datetime import date
from decimal import Decimal

from sqlalchemy import Table, Column, Integer, String, DECIMAL, Float, Date

Base = declarative_base()

# Product Model for database of products known
class Product(Base):
	__tablename__ = "product"

	product_id = Column(Integer, primary_key=True)
	product_name = Column(String(100), nullable=False)
	barcode = Column(String(64), unique=True, nullable=False)
	price = Column(DECIMAL(10,2), nullable=False)
	net_weight = Column(Float, nullable=False)

	# Human-readable column names
	COLUMN_LABELS = {
		"product_id": "Product ID",
		"product_name": "Product Name",
		"barcode": "Barcode",
		"price": "Price",
		"net_weight": "Net Weight (g)",
	}

# Transaction Model for 'inventory'
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

Base.metadata.create_all(engine)

# Lookup barcode function to centralize a bit
def lookup_barcode(session, barcode):
	return session.query(Product).filter_by(barcode=barcode).first()

def get_all_products(session):
	return session.query(Product).all()

# Eager load 'product' relationship using joinedload so we can safely access transaction.product.* fields in templates
# after session is closed (avoids DetachedInstanceError)
def get_all_transactions(session):
	return session.query(Transaction).options(joinedload(Transaction.product)).all()

#####################################
# Uses **kwargs to take in optional data (ie., from forms)
# Now used for scanner barcode input only
def process_scanned_barcode(session, barcode, **product_data):
	product = lookup_barcode(session, barcode)

	if product:
		add_transaction(session, product, quantity=1, price_at_scan=product.price, net_weight=product.net_weight)
		return "added_transaction"

	return "new_product"
####################################

def ensure_product_exists(session, barcode, **product_data):
	product = lookup_barcode(session, barcode)
	if not product:
		add_product(session, barcode, **product_data)

# Add not-previously-encountered product
def add_product(session, barcode, **product_data):
	product = Product(
		barcode=barcode,
		product_name=product_data["product_name"], 
		price=Decimal(product_data["price_at_scan"]),
		net_weight=float(product_data["net_weight"])
	)

	session.add(product)

# Add product to 'inventory'
def add_transaction(session, product, **product_data):
	today = date.today()
	quantity = int(product_data.get("quantity") or 1)
	
	# Check to determine whether to increment qty or add new instance
	transaction = session.query(Transaction).filter_by(
		product_id=product.product_id,
		date_scanned=today
	).first()
	
	if transaction:
		transaction.quantity += quantity
	else:
		transaction = Transaction(
			product_id=product.product_id,
			price_at_scan=Decimal(product_data["price_at_scan"]),
			quantity=quantity,
			date_scanned=today
		)
		session.add(transaction)