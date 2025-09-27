# Handles DB models for grocery module
import enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app._infra.db_base import Base

from app.modules.groceries.constants import (
       PRODUCT_NAME_MAX_LENGTH, BARCODE_MAX_LENGTH, 
       NET_WEIGHT_PRECISION, NET_WEIGHT_SCALE,
       CALORIES_PRECISION, CALORIES_SCALE,
       PRICE_PRECISION, PRICE_SCALE,
	   SHOPPING_LIST_NAME_MAX_LENGTH
   )

class UnitEnum(enum.Enum):
	G = "G"
	KG = "KG"
	OZ = "OZ"
	LB = "LB"
	ML = "ML"
	L = "L"
	FL_OZ = "FL_OZ"
	EA = "EA" 	# each
	
class ProductCategoryEnum(enum.Enum):
    FRUITS = "FRUITS"
    VEGETABLES = "VEGETABLES"
    LEGUMES = "LEGUMES" # beans, lentils, peas
    GRAINS = "GRAINS" # rice, oats, pasta (I rarely eat pasta, so it's either so uncommon I'd be fine throwing it here OR a restaurant/prepped food anyway)
    BAKERY = "BAKERY"
    DAIRY_EGGS = "DAIRY_EGGS"
    MEATS = "MEATS"
    SEAFOOD = "SEAFOOD"
    FATS_OILS = "FATS_OILS" # Cooking oils, butter, avocado, nuts / nut butters
    SNACKS = "SNACKS"
    SWEETS = "SWEETS"
    BEVERAGES = "BEVERAGES"
    CONDIMENTS_SAUCES = "CONDIMENTS_SAUCES"
    PROCESSED_CONVENIENCE = "PROCESSED_CONVENIENCE" # Restaurant, fast food, frozen meals, packaged stuff. This is the “buddy, don’t live here” category
    SUPPLEMENTS = "SUPPLEMENTS" # Protein powder, bars, vitamins, creatine, etc.
	

class Product(Base):
	"""Acts as a catalog of 'known' products and includes more static data regarding the product."""

	name = Column(
		String(PRODUCT_NAME_MAX_LENGTH),
		nullable=False
	)
	
	category = Column(
		SAEnum(ProductCategoryEnum, name="product_category_enum"),
		nullable=False
	)
	
	barcode = Column(
		String(BARCODE_MAX_LENGTH),
		unique=True,
		nullable=False
	)

	net_weight = Column(
		Numeric(NET_WEIGHT_PRECISION, NET_WEIGHT_SCALE),
		nullable=False
	)
	
	unit_type = Column(
		SAEnum(UnitEnum, name="unit_enum", values_callable=lambda x: [e.value for e in x]),
		nullable=False,
		default=UnitEnum.G
	)

	calories_per_100g = Column(
		Numeric(CALORIES_PRECISION, CALORIES_SCALE),
		CheckConstraint('calories_per_100g >= 0', name='ck_product_calories_non_negative'),
		nullable=True
	)
	
	deleted_at = Column(DateTime(timezone=True), nullable=True)

	def __str__(self):
		return f"{self.name} ({self.barcode})"
	
	def __repr__(self):
		return f"<Product id={self.id} name='{self.name}' barcode='{self.barcode}'>"


class Transaction(Base):
	"""Acts as 'instance of buying a given item'."""

	product_id = Column(
		Integer, ForeignKey("product.id"),
		nullable=False
	)
	
	price_at_scan = Column(
		Numeric(PRICE_PRECISION, PRICE_SCALE),
		CheckConstraint('price_at_scan >= 0', name='ck_transaction_price_non_negative'),
		nullable=False
	)
	
	quantity = Column(
		Integer,
		CheckConstraint('quantity > 0', name='ck_transaction_quantity_positive'),
		nullable=False
	)

	product = relationship("Product")

	def __str__(self):
		return f"Transaction:{self.id}: {self.quantity}x {self.product.name} @ {self.price_at_scan}"
	
	def __repr__(self):
		return f"<Transaction id={self.id} product_id={self.product_id}>"


class ShoppingList(Base):
    """Provides entrypoint for working with shoppinglistitems for a given list."""

    name = Column(
        String(SHOPPING_LIST_NAME_MAX_LENGTH),
        default="Current List"
    )

    items = relationship("ShoppingListItem", back_populates="shopping_list")


class ShoppingListItem(Base):
	"""Items in the list. Effectively acts as a pointer to the actual product item itself."""

	quantity_wanted = Column(
		Integer,
		CheckConstraint('quantity_wanted > 0', name='ck_shopping_quantity_wanted_positive'),
		nullable=False,
		default=1
	)
	
	shopping_list_id = Column(
		Integer,
		ForeignKey('shoppinglist.id'),
		nullable=False
	)
	
	product_id = Column(
		Integer,
		ForeignKey('product.id'),
		nullable=False
	)

	shopping_list = relationship("ShoppingList", back_populates="items")
	product = relationship("Product")