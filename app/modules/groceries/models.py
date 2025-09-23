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

# Acts as our catalog of "known" products
class Product(Base):

	name = Column(String(100), nullable=False)
	category = Column(String(100), nullable=True) # eg, dairy, produce
	barcode = Column(String(64), unique=True, nullable=False) # TODO: Change to 16 to match validation/reqs

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

# Essentially our container for shoppinglistitems, provides an entrypoint for working with shoppinglistitems for a given list
class ShoppingList(Base):
	name = Column(String(100), default="Current List")

	items = relationship("ShoppingListItem", back_populates="shopping_list")

# Actual items in the list
# Note to self: Effectively acts as a pointer to the actual product item itself
class ShoppingListItem(Base):

	quantity_wanted = Column(Integer, nullable=False, default=1)
	shopping_list_id = Column(Integer, ForeignKey('shoppinglist.id'), nullable=False)
	product_id = Column(Integer, ForeignKey('product.id'), nullable=False)

	# Relationships
	shopping_list = relationship("ShoppingList", back_populates="items")
	product = relationship("Product")