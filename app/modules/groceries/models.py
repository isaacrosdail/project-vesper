# Handles DB models for grocery module
import enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app._infra.db_base import Base


class Unit(enum.Enum):
	g = "g"
	kg = "kg"
	oz = "oz"
	lb = "lb"
	ml = "ml"
	l = "l"
	fl_oz = "fl_oz"
	ea = "ea" 	# each

# Acts as catalog of 'known' products
# TODO: Sort out logic for "re-adding a product that is marked as having been soft-deleted"
#		ie, "un-soft-delete it"
class Product(Base):

	name = Column(String(100), nullable=False)
	category = Column(String(100), nullable=True) # eg, dairy, produce
	barcode = Column(String(64), unique=True, nullable=False)

	net_weight = Column(Numeric(10, 3), nullable=False) # "asdecimal" false?
	unit_type = Column(SAEnum(Unit, name="unit_enum"), nullable=False, default=Unit.g)

	calories_per_100g = Column(Numeric(8, 2), nullable=True)
	deleted_at = Column(DateTime(timezone=True), nullable=True)

	def __str__(self):
		return f"{self.name} ({self.barcode})"
	
	def __repr__(self):
		return (
			f"<Product id={self.id} name='{self.name}' "
			f"<barcode='{self.barcode}'>"
		)

# Transaction Model for 'inventory'
class Transaction(Base):

	product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
	price_at_scan = Column(Numeric(10,2), nullable=False)
	quantity = Column(Integer, nullable=False)

	product = relationship("Product")

	def __str__(self):
		return f"Transaction:{self.id}: {self.quantity}x {self.product.name} @ {self.price_at_scan}"
	
	def __repr__(self):
		return f"<Transaction id={self.id} product_id={self.product_id}>"

	# Human-readable column names
	COLUMN_LABELS = {
		"id": "ID",
		"product_id": "Product ID",
		"price_at_scan": "Price",
		"quantity": "Quantity",
		"created_at": "Created",
	}