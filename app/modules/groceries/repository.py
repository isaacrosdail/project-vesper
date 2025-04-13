## DB logic functions to access data

from .models import Product, Transaction
from sqlalchemy.orm import Session, joinedload
from datetime import date
from decimal import Decimal

# Debug print
print(" grocery_repo.py imported")

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

def ensure_product_exists(session, **product_data):
	barcode = product_data["barcode"]
	product = lookup_barcode(session, barcode)
	if not product:
		add_product(session, **product_data)

# Add not-previously-encountered product
def add_product(session, **product_data):

	# Minimal, strict input validation
	if not product_data.get("barcode"):
		raise ValueError("Barcode is required.")
	if not product_data.get("product_name"):
		raise ValueError("Product name is required.")
	if "price" not in product_data or Decimal(product_data["price"]) < 0:
		raise ValueError("Price must be provided and non-negative.")
	if "net_weight" not in product_data or float(product_data["net_weight"]) <= 0:
		raise ValueError("Net weight must be positive.")

	product = Product(
		barcode=product_data["barcode"],
		product_name=product_data["product_name"],
		price=Decimal(product_data["price"]),
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
			price_at_scan=Decimal(product_data["price"]),
			quantity=quantity,
			date_scanned=today
		)
		session.add(transaction)