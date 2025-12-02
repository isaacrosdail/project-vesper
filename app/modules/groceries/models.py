# Handles DB models for grocery module
import enum
from decimal import Decimal
from datetime import datetime
from typing import Self

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, CheckConstraint, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app._infra.db_base import Base
from app.shared.serialization import APISerializable
from app.shared.types import OrderedEnum

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
    LEGUMES = "LEGUMES"
    GRAINS = "GRAINS"
    BAKERY = "BAKERY"
    DAIRY_EGGS = "DAIRY_EGGS"
    MEATS = "MEATS"
    SEAFOOD = "SEAFOOD"
    FATS_OILS = "FATS_OILS"
    SNACKS = "SNACKS"
    SWEETS = "SWEETS"
    BEVERAGES = "BEVERAGES"
    CONDIMENTS_SAUCES = "CONDIMENTS_SAUCES"
    PROCESSED_CONVENIENCE = "PROCESSED_CONVENIENCE"
    SUPPLEMENTS = "SUPPLEMENTS"
	
    def __lt__(self, other: Self) -> bool:
        return self.value < other.value


class Product(Base, APISerializable):
    """Acts as a catalog of 'known' products and includes the more 'static' data about the product."""

    __table_args__ = (
        CheckConstraint('calories_per_100g >= 0', name='ck_product_calories_non_negative'),
        UniqueConstraint('user_id', 'name', name='uq_user_product_name'),
        UniqueConstraint('user_id', 'barcode', name='uq_user_product_barcode'),
    )

    name: Mapped[str] = mapped_column(
        String(PRODUCT_NAME_MAX_LENGTH),
        nullable=False
    )

    category: Mapped[ProductCategoryEnum] = mapped_column(
        SAEnum(ProductCategoryEnum, name="product_category_enum"),
        nullable=False
    )

    barcode: Mapped[str] = mapped_column(
        String(BARCODE_MAX_LENGTH),
        nullable=True
    )

    net_weight: Mapped[Decimal] = mapped_column(
        Numeric(NET_WEIGHT_PRECISION, NET_WEIGHT_SCALE),
        nullable=False
    )

    unit_type: Mapped[UnitEnum] = mapped_column(
        SAEnum(UnitEnum, name="unit_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UnitEnum.G
    )

    calories_per_100g: Mapped[Decimal] = mapped_column(
        Numeric(CALORIES_PRECISION, CALORIES_SCALE),
        nullable=True
    )

    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.barcode})"

    def __repr__(self) -> str:
        return f"<Product id={self.id} name='{self.name}' barcode='{self.barcode}'>"


class Transaction(Base, APISerializable):
    """Acts as 'instance of buying a given item'."""

    __table_args__ = (
        CheckConstraint('price_at_scan >= 0', name='ck_transaction_price_non_negative'),
        CheckConstraint('quantity > 0', name='ck_transaction_quantity_positive'),
    )

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"),
        nullable=False
    )

    price_at_scan: Mapped[Decimal] = mapped_column(
        Numeric(PRICE_PRECISION, PRICE_SCALE),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    product = relationship("Product")

    @property
    def product_name(self) -> str | None:
        return self.product.name if self.product else None

    @property
    def price_per_100g(self) -> Decimal:
        weight_decimal = Decimal(str(self.product.net_weight))
        return (self.price_at_scan / weight_decimal) * 100

    def __str__(self) -> str:
        product_name = self.product.name if self.product else f"Product #{self.product_id}"
        return f"Transaction:{self.id}: {self.quantity}x {product_name} @ {self.price_at_scan}"

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} product_id={self.product_id}>"


class ShoppingList(Base, APISerializable):
    """Provides entrypoint for working with shoppinglistitems for a given list."""

    name: Mapped[str] = mapped_column(
        String(SHOPPING_LIST_NAME_MAX_LENGTH),
        default="Current List"
    )

    items = relationship("ShoppingListItem", back_populates="shopping_list")


class ShoppingListItem(Base, APISerializable):
    """Items in the list. Effectively acts as a pointer to the actual product item itself."""

    __table_args__ = (
        CheckConstraint('quantity_wanted > 0', name='ck_shopping_quantity_wanted_positive'),
    )

    quantity_wanted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    shopping_list_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('shopping_lists.id'),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('products.id'),
        nullable=False
    )

    shopping_list = relationship("ShoppingList", back_populates="items")
    product = relationship("Product")