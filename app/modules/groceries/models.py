# Handles DB models for grocery module
from datetime import datetime, time
from decimal import Decimal
from enum import StrEnum, auto
from typing import Any, ClassVar, Self

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.shared.serialization import APISerializable

BARCODE_MIN_LENGTH = 8
BARCODE_MAX_LENGTH = 32
# Barcode
# Alphanumeric for UPC/QR/UUID support
BARCODE_REGEX = rf"^[A-Za-z0-9]{{{BARCODE_MIN_LENGTH},{BARCODE_MAX_LENGTH}}}$"
NET_WEIGHT_PRECISION = 7
NET_WEIGHT_SCALE = 3
PRICE_PRECISION = 7
PRICE_SCALE = 2
PRODUCT_NAME_MAX_LENGTH = 80
SHOPPING_LIST_NAME_MAX_LENGTH = 64
RECIPE_NAME_MAX_LENGTH = 100


class UnitEnum(StrEnum):
    G = auto()
    KG = auto()
    OZ = auto()
    LB = auto()
    ML = auto()
    L = auto()
    FL_OZ = auto()
    EA = auto()  # each

    @property
    def label(self) -> str:
        return self.replace("_", " ")


class ProductCategoryEnum(StrEnum):
    FRUITS = auto()
    VEGETABLES = auto()
    LEGUMES = auto()
    GRAINS = auto()
    BAKERY = auto()
    DAIRY_EGGS = auto()
    MEATS = auto()
    SEAFOOD = auto()
    FATS_OILS = auto()
    SNACKS = auto()
    SWEETS = auto()
    BEVERAGES = auto()
    CONDIMENTS_SAUCES = auto()
    PROCESSED_CONVENIENCE = auto()
    SUPPLEMENTS = auto()

    @property
    def label(self) -> str:
        return self.name.replace("_", " & ").title()


class Product(Base, APISerializable):
    """Acts as a catalog of 'known' products and includes the more 'static' data about the product."""

    __table_args__ = (
        CheckConstraint(
            "calories_per_100g >= 0", name="ck_product_calories_non_negative"
        ),
        UniqueConstraint("user_id", "name", name="uq_user_product_name"),
        UniqueConstraint("user_id", "barcode", name="uq_user_product_barcode"),
        Index("ix_products_user_deleted_at", "user_id", "deleted_at"),
    )

    name: Mapped[str] = mapped_column(String(PRODUCT_NAME_MAX_LENGTH), nullable=False)

    category: Mapped[ProductCategoryEnum] = mapped_column(
        SAEnum(ProductCategoryEnum, name="product_category_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    barcode: Mapped[str | None] = mapped_column(String(BARCODE_MAX_LENGTH), nullable=True)

    net_weight: Mapped[Decimal] = mapped_column(
        Numeric(NET_WEIGHT_PRECISION, NET_WEIGHT_SCALE), nullable=False
    )

    unit_type: Mapped[UnitEnum] = mapped_column(
        SAEnum(
            UnitEnum, name="unit_enum", values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=UnitEnum.G,
        server_default="g"
    )

    calories_per_100g: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    protein_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_mono_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_poly_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_sat_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_fiber_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_sugar_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sodium_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    potassium_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="products")
    inventory: Mapped["ProductInventory"] = relationship(back_populates="product")
    ledger_entries: Mapped[list["InventoryLedger"]] = relationship(back_populates="product")

    def __str__(self) -> str:
        return f"{self.name} ({self.barcode})"

    def __repr__(self) -> str:
        return f"<Product id={self.id} name='{self.name}' barcode='{self.barcode}'>"


class ShoppingTrip(Base):
    """Cluster of transactions"""
    # date, store_name, total_price?
    entry_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    store_name: Mapped[str] = mapped_column(String(50), nullable=False)

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(PRICE_PRECISION, PRICE_SCALE), nullable=False
    )

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="shopping_trip")


class Transaction(Base, APISerializable):
    """Acts as 'instance of buying a given item'."""

    __api_exclude__: ClassVar[list[str]] = []

    __api_properties__: ClassVar[list[str]] = ["price_per_100g"]

    def to_api_dict(self, *, include_relations: bool = False) -> dict[str, Any]:
        result = super().to_api_dict(include_relations=include_relations)
        result["product_name"] = self.product.name
        return result

    __table_args__ = (
        CheckConstraint("price_at_scan >= 0", name="ck_transaction_price_non_negative"),
        CheckConstraint("quantity > 0", name="ck_transaction_quantity_positive"),
        Index("ix_transactions_user_created_at", "user_id", "created_at"),
    )

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )

    shopping_trip_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("shopping_trips.id"), nullable=True
    )

    price_at_scan: Mapped[Decimal] = mapped_column(
        Numeric(PRICE_PRECISION, PRICE_SCALE), nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    user = relationship("User", back_populates="transactions")
    product = relationship("Product", lazy="joined")
    shopping_trip: Mapped["ShoppingTrip | None"] = relationship(back_populates="transactions")

    @property
    def product_name(self) -> str | None:
        return self.product.name if self.product else None

    @property
    def price_per_100g(self) -> Decimal:
        weight_decimal = Decimal(str(self.product.net_weight))
        return (self.price_at_scan / weight_decimal) * 100

    def __str__(self) -> str:
        product_name = (
            self.product.name if self.product else f"Product #{self.product_id}"
        )
        return f"Transaction:{self.id}: {self.quantity}x {product_name} @ {self.price_at_scan}"

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} product_id={self.product_id}>"


class ShoppingList(Base, APISerializable):
    """Provides entrypoint for working with shoppinglistitems for a given list."""

    name: Mapped[str] = mapped_column(
        String(SHOPPING_LIST_NAME_MAX_LENGTH), default="Current List"
    )

    user = relationship("User", back_populates="shopping_list")
    items = relationship("ShoppingListItem", back_populates="shopping_list", lazy="raise")

    def __repr__(self) -> str:
        return f"<ShoppingList id={self.id} name={self.name} items_count={len(self.items)}>"


class ShoppingListItem(Base, APISerializable):
    """Items in the list. Effectively acts as a pointer to the actual product item itself."""

    __api_exclude__: ClassVar[list[str]] = []

    def to_api_dict(self, *, include_relations: bool = False) -> dict[str, Any]:
        result = super().to_api_dict(include_relations=include_relations)
        result["product_name"] = self.product.name
        return result

    __table_args__ = (
        CheckConstraint(
            "quantity_wanted > 0", name="ck_shopping_quantity_wanted_positive"
        ),
    )

    quantity_wanted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # TODO: Currently for UI state, will inform future "Complete shopping list" calculations
    is_checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    shopping_list_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shopping_lists.id"), nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )

    user = relationship("User", back_populates="shopping_list_item")
    shopping_list = relationship("ShoppingList", back_populates="items")
    product = relationship("Product", lazy="joined")

    def __repr__(self) -> str:
        return f"<ShoppingListItem id={self.id} product={self.product.name!r} qty={self.quantity_wanted}>"


class Recipe(Base, APISerializable):
    """Represents individual recipe, itself consisting of ????"""

    __table_args__ = (
        CheckConstraint(
            "yields > 0", name="ck_recipe_yields_positive"
        ),
    )

    name: Mapped[str] = mapped_column(
        String, nullable=False
    )

    yields: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    yields_units: Mapped[UnitEnum] = mapped_column(
        SAEnum(
            UnitEnum, name="unit_enum", values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=UnitEnum.G,
        server_default="g"
    )

    user = relationship("User", back_populates="recipes")
    ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        lazy="raise"
    )

class RecipeIngredient(Base, APISerializable):
    """Represents single ingredient in a given Recipe (list)"""

    __table_args__ = (
        CheckConstraint(
            "amount_value > 0", name="ck_recipe_ingredient_amount_value_positive"
        ),
    )

    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id"), nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )

    amount_value: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    amount_units: Mapped[UnitEnum] = mapped_column(
        SAEnum(
            UnitEnum, name="unit_enum", values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=UnitEnum.G,
        server_default="g"
    )

    recipe = relationship("Recipe", back_populates="ingredients")
    product = relationship("Product", lazy="joined")


class MealEnum(StrEnum):
    BREAKFAST = auto()
    MORNING_SNACK = auto()
    LUNCH = auto()
    AFTERNOON_SNACK = auto()
    SUPPER = auto()
    PM_SNACK = auto()

    @property
    def label(self) -> str:
        return self.replace("_", " ").title()

    # Builds reverse map once?
    # enum vals ARE lowercase underscored versions (from auto())
    # and labels here are the title-cased spaced versions. So we
    # just reverse the transform:
    # "Afternoon Snack" -> "afternoon_snack" -> MealEnum("afternoon_snack") -> MealEnum.AFTERNOON_SNACK
    @classmethod
    def from_label(cls, label: str) -> Self:
        return cls(label.lower().replace(" ", "_"))

# NOTE: Assuming specific times in user's local tz. Export data only
# includes date iso
MEAL_TIMES = {
    MealEnum.BREAKFAST: time(8, 0),
    MealEnum.MORNING_SNACK: time(10, 0),
    MealEnum.LUNCH: time(12, 0),
    MealEnum.AFTERNOON_SNACK: time(15, 0),
    MealEnum.PM_SNACK: time(17, 0),
    MealEnum.SUPPER: time(19, 0),
}

NUMERIC_MAPPINGS = {
    "Calories": "calories",
    "Fat (g)": "fat",
    "Saturated Fat": "fat_sat",
    "Polyunsaturated Fat": "fat_poly",
    "Monounsaturated Fat": "fat_mono",
    "Sodium (mg)": "sodium",
    "Potassium": "potassium",
    "Carbohydrates (g)": "carbs",
    "Fiber": "carbs_fiber",
    "Sugar": "carbs_sugar",
    "Protein (g)": "protein",
}

class NutritionLog(Base, APISerializable):

    __table_args__ = (
        Index("ix_nutrition_logs_user_entry_datetime", "user_id", "entry_datetime"),
    )

    entry_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    meal: Mapped[MealEnum] = mapped_column(
        SAEnum(
            MealEnum, name="meal_enum", values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False
    )

    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_mono: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_poly: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_sat: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_fiber: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_sugar: Mapped[float | None] = mapped_column(Float, nullable=True)

    sodium: Mapped[float | None] = mapped_column(Float, nullable=True)
    potassium: Mapped[float | None] = mapped_column(Float, nullable=True)



class InventoryLedgerEventTypeEnum(StrEnum):
    PURCHASE = auto()    # logging a txn
    CONSUMPTION = auto() # logging a meal / NutritionLog
    CORRECTION = auto()  # manual "actually i have 3 of these" override
    WASTE = auto()       # "threw out expired beef"


class InventoryLedger(Base):

    __table_args__ = (
        Index("ix_inventory_ledger_product_created", "product_id", "created_at"),
    )
    # product_id fkey
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="ledger_entries", lazy="joined")
    # qty_delta (negative for consumption)
    qty_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    # event_type (enum: purchase, correction, waste, consumption)
    event_type: Mapped[InventoryLedgerEventTypeEnum] = mapped_column(
        SAEnum(
            InventoryLedgerEventTypeEnum, name="inventory_event_type_enum", values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False
    )
    # note (optional obv, "expired" for waste events)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ProductInventory(Base):
    # Cached current inventory state
    # product_id fkkey, unique per user
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, unique=True) # unique so each product has ONE inventory record ofc
    product: Mapped["Product"] = relationship(back_populates="inventory", lazy="joined") # one-to-one, sqlalchemy infers cardinality from the type annotation: thing vs list[thing]
    # qty_on_hand (current stock ofc)
    qty_on_hand: Mapped[int] = mapped_column(Integer, nullable=False)
