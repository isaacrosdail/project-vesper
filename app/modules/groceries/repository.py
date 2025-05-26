## DB logic functions to access data
# The "talk to the database - and nothing else" layer

from .models import Product, Transaction
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from decimal import Decimal

# Lookup barcode function to centralize a bit
def lookup_barcode(session, barcode):
	return session.query(Product).filter_by(barcode=barcode).first()
  
def get_all_products(session):
	return session.query(Product).all()

# Eager load 'product' relationship using joinedload so we can safely access transaction.product.* fields in templates
# after session is closed (avoids DetachedInstanceError)
def get_all_transactions(session):
	return session.query(Transaction).options(joinedload(Transaction.product)).all()

def ensure_product_exists(session, **product_data):
	barcode = product_data["barcode"]
	product = lookup_barcode(session, barcode)
	if not product:
		add_product(session, **product_data)

# Add product to product catalog
def add_product(session, **product_data):

	# Minimal, strict input validation
	if not product_data.get("barcode"):
		raise ValueError("Barcode is required.")
	if not product_data.get("product_name"):
		raise ValueError("Product name is required.")
	if "net_weight" not in product_data or float(product_data["net_weight"]) <= 0:
		raise ValueError("Net weight must be positive.")
	
	# TEMPORARY price hack to avoid issues if field still exists (Need to sort later)
	price = product_data.get("price")
	if "price" in Product.__table__.columns:
		if price is None:
			price = Decimal("0.00")
		else:
			price = Decimal(price)

	product = Product(
		barcode=product_data["barcode"],
		product_name=product_data["product_name"],
		net_weight=float(product_data["net_weight"]),
		price=price if "price" in Product.__table__.columns else None  # ← handles the zombie field
	)

	session.add(product)

# Add product to transactions list
def add_transaction(session, product, **product_data):

	if product is None:
		raise ValueError("Product must be provided for transaction.")
	
	today = datetime.now(timezone.utc).date()
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
			price_at_scan=Decimal(product_data["price"]),
			quantity=quantity,
			date_scanned=today
		)
		session.add(transaction)