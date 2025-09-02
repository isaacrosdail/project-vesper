"""
Repository layer for groceries module.
"""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import joinedload

from app.modules.groceries.models import Product, Transaction, Unit
from app.shared.datetime.helpers import today_range
from app.shared.repository.base import BaseRepository


class GroceriesRepository(BaseRepository):

	def get_product_by_barcode(self, barcode: str):
		return self.session.query(Product).filter(
			Product.barcode == barcode,
			Product.user_id == self.user_id,
			Product.deleted_at.is_(None) # TODO: Needed if we have safe_delete now?
		).first()
	
	def get_all_products(self):
		"""Get all products for current user."""
		return self.session.query(Product).filter(
			Product.deleted_at.is_(None),
			Product.user_id == self.user_id
		).all()

	# TODO: NOTES: Eager load 'product' relationship using joinedload so we can safely access transaction.product.* fields in templates
	# after session is closed (avoids DetachedInstanceError)
	def get_all_transactions(self):
		"""Get all transaction for current user with eager-loaded products."""
		return self.session.query(Transaction).options(
			joinedload(Transaction.product)
		).filter(
			Transaction.user_id == self.user_id
		).all()

	def get_transaction_in_window(self, product_id: int, start_utc: datetime, end_utc: datetime):
		"""Get a transaction within a certain datetime window (UTC)."""
		return self.session.query(Transaction).filter(
			Transaction.product_id == product_id,
			Transaction.created_at >= start_utc,
			Transaction.created_at < end_utc,
			Transaction.user_id == self.user_id
		).first()

	def get_or_create_product(self, **product_data):
		"""Get existing product or create new one. Returns tuple (product, was_created)."""
		barcode = product_data["barcode"]
		product = self.get_product_by_barcode(barcode)
		if product:
			return product, False
		return self.create_product(**product_data), True

	def create_product(self, **product_data) -> Product:
		product = Product(
			barcode=product_data["barcode"],
			name=product_data["name"],
			category=product_data["category"],
			net_weight=float(product_data["net_weight"]),
			unit_type=Unit(product_data["unit_type"]),
			calories_per_100g=float(product_data["calories_per_100g"]),
			user_id=self.user_id
		)
		self.session.add(product)
		return product
		
	def create_transaction(self, product, **product_data):
		# TODO: belongs in VALIDATORS!
		if product is None:
			raise ValueError("Product must be provided for transaction.")
		
		quantity = int(product_data.get("quantity") or 1)

		new_transaction = Transaction(
			product_id=product.id,
			price_at_scan=Decimal(product_data["price"]),
			quantity=quantity,
			created_at=datetime.now(timezone.utc),
			user_id=self.user_id
		)
		self.session.add(new_transaction)
		return new_transaction

	def increment_transaction_quantity(self, transaction: Transaction, quantity: int = 1):
		"""Add quantity to an existing transaction."""
		transaction.quantity += quantity
		return transaction

	def add_or_increment_transaction(self, product, **product_data):
		"""
		Add transaction or increment existing one in today's window.
		Returns (transaction, was_created)
		"""
		if product is None:
			raise ValueError("Product must be provided for transaction.")
		start_utc, end_utc = today_range()
		existing = self.get_transaction_in_window(product.id, start_utc, end_utc)
		quantity = int(product_data.get("quantity") or 1)

		if existing:
			self.increment_transaction_quantity(existing, quantity)
			return existing, False
		else:
			new_transaction = self.create_transaction(product, **product_data)
			return new_transaction, True