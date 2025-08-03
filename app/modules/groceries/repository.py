## DB logic functions to access data
# The "talk to the database - and nothing else" layer

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import joinedload

from .models import Product, Transaction


# Lookup barcode function to centralize a bit
# Note: For the two functions here, we're now filtering out "soft-deleted" items
def lookup_barcode(session, barcode, user_id):
	return session.query(Product).filter(
		Product.barcode == barcode,
		Product.user_id == user_id,
		Product.deleted_at.is_(None)
	).first()
  
def get_user_products(session, user_id):
	return session.query(Product).filter(
		Product.deleted_at.is_(None),
		Product.user_id == user_id
	).all()

# Eager load 'product' relationship using joinedload so we can safely access transaction.product.* fields in templates
# after session is closed (avoids DetachedInstanceError)
def get_user_transactions(session, user_id):
	return session.query(Transaction).options(joinedload(Transaction.product)).filter(
		Transaction.user_id == user_id
	).all()

def get_user_transaction_for_date(session, user_id, product_id, date):
	return session.query(Transaction).filter(
		Transaction.product_id==product_id,
		Transaction.created_at==date,
		Transaction.user_id==user_id
	).first()

def get_or_create_product(session, user_id, **product_data):
	barcode = product_data["barcode"]
	product = lookup_barcode(session, barcode, user_id)
	if not product:
		add_product(session, user_id, **product_data)

# Add product to product catalog
def add_product(session, user_id, **product_data):
	# Note: Validation should be done by caller (ie, route)
	product = Product(
		barcode=product_data["barcode"],
		product_name=product_data["product_name"],
		category=product_data["category"],
		net_weight=float(product_data["net_weight"]),
		# price=price if "price" in Product.__table__.columns else None  # ← handles the zombie field
		unit_type=product_data["unit_type"],
		calories_per_100g=float(product_data["calories_per_100g"]),
		user_id=user_id
	)
	session.add(product)

# Add product to transactions list
def add_transaction(session, product, user_id, **product_data):

	if product is None:
		raise ValueError("Product must be provided for transaction.")
	
	today_utc = datetime.now(timezone.utc).date()
	quantity = int(product_data.get("quantity") or 1)
	
	# Check to determine whether to increment qty or add new instance
	existing_transaction = get_user_transaction_for_date(session, user_id, product.id, today_utc)
	
	if existing_transaction:
		existing_transaction.quantity += quantity
	else:
		new_transaction = Transaction(
			product_id=product.id,
			price_at_scan=Decimal(product_data["price"]),
			quantity=quantity,
			created_at=today_utc,
			user_id=user_id
		)
		session.add(new_transaction)