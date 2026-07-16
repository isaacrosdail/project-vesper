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

BARCODE_MIN_LENGTH = 8
BARCODE_MAX_LENGTH = 32
# Barcode
# Alphanumeric for UPC/QR/UUID support
BARCODE_REGEX = rf"^[A-Za-z0-9]{{{BARCODE_MIN_LENGTH},{BARCODE_MAX_LENGTH}}}$"
NET_WEIGHT_PRECISION = 7
NET_WEIGHT_SCALE = 3
QTY_PRECISION = 12
QTY_SCALE = 3
PRICE_PRECISION = 7
PRICE_SCALE = 2
PRODUCT_NAME_MAX_LENGTH = 80
SHOPPING_LIST_NAME_MAX_LENGTH = 64
RECIPE_NAME_MAX_LENGTH = 100


class DimensionEnum(StrEnum):
    MASS = auto()
    VOLUME = auto()
    COUNT = auto()

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

    @property
    def factor(self) -> Decimal:
        """Defines the conversion factor to multiply by to reach the unit's base unit.
        'g' for MASS units, 'ml' for volume units.
        """
        return _FACTOR_MAPPINGS[self]

    @property
    def dimension(self) -> DimensionEnum:
        return _UNIT_DIMENSION[self]

_FACTOR_MAPPINGS = {
    UnitEnum.G: Decimal(1), UnitEnum.KG: Decimal(1000), UnitEnum.OZ: Decimal("28.3495"), UnitEnum.LB: Decimal("453.592"),
    UnitEnum.ML: Decimal(1), UnitEnum.L: Decimal(1000), UnitEnum.FL_OZ: Decimal("29.5735"), UnitEnum.EA: Decimal(1)
}

_DIMENSION_GROUPS = {
    DimensionEnum.MASS: { UnitEnum.G, UnitEnum.KG, UnitEnum.OZ, UnitEnum.LB },
    DimensionEnum.VOLUME: { UnitEnum.ML, UnitEnum.L, UnitEnum.FL_OZ },
    DimensionEnum.COUNT: { UnitEnum.EA },
}
_UNIT_DIMENSION = {unit: dim for dim, units in _DIMENSION_GROUPS.items() for unit in units }
assert _UNIT_DIMENSION.keys() == set(UnitEnum)

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

_NUTRITION_FIELDS = ("calories", "protein", "fat", "carbs", "fat_mono", "fat_poly", "fat_sat",
        "carbs_fiber", "carbs_sugar", "sodium", "potassium")

def _non_negative_sql(cols: tuple[str, ...]) -> str:
    return " AND ".join(f"({c} IS NULL OR {c} >= 0)" for c in cols)

class Product(Base):
    """Acts as a catalog of 'known' products and includes the more 'static' data about the product."""

    __table_args__ = (
        CheckConstraint(
            _non_negative_sql(tuple(f"{f}_per_100g" for f in _NUTRITION_FIELDS)),
            name="nutrition_non_negative",
        ),
        CheckConstraint(
            "net_weight > 0", name="ck_product_net_weight_positive",
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

    __table_args__ = (
        CheckConstraint("total_price >= 0", name="total_price_non_negative"),
    )
    # date, store_name, total_price?
    entry_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    store_name: Mapped[str] = mapped_column(String(50), nullable=False)

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(PRICE_PRECISION, PRICE_SCALE), nullable=False
    )

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="shopping_trip")


class Transaction(Base):
    """Acts as 'instance of buying a given item'."""

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


class ShoppingList(Base):
    """Provides entrypoint for working with shoppinglistitems for a given list."""

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_shopping_list"),
    )

    name: Mapped[str] = mapped_column(
        String(SHOPPING_LIST_NAME_MAX_LENGTH), default="Current List"
    )

    user = relationship("User", back_populates="shopping_list")
    items = relationship("ShoppingListItem", back_populates="shopping_list", lazy="raise")

    def __repr__(self) -> str:
        return f"<ShoppingList id={self.id} name={self.name} items_count={len(self.items)}>"


class ShoppingListItem(Base):
    """Items in the list. Effectively acts as a pointer to the actual product item itself."""

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


class Recipe(Base):
    """Represents individual recipe, itself consisting of ????"""

    __table_args__ = (
        CheckConstraint(
            "yields > 0", name="ck_recipe_yields_positive"
        ),
    )

    name: Mapped[str] = mapped_column(
        String(RECIPE_NAME_MAX_LENGTH), nullable=False
    )

    yields: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False
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

class RecipeIngredient(Base):
    """Represents single ingredient in a given Recipe (list)"""

    __table_args__ = (
        UniqueConstraint("recipe_id", "product_id", name="uq_recipe_ingredient_recipe_product"),
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

    amount_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False
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

    @property
    def grams(self) -> Decimal:
        return self.amount_value * self.amount_units.factor

    @property
    def nutrition_contribution(self) -> dict[str, Decimal]:
        per_100 = self.grams / 100
        # return dict of "calories": VAL, etc for NutritionLog to consume?
        return {
            name: per_100 * Decimal(str(getattr(self.product, f"{name}_per_100g") or 0))
            for name in _NUTRITION_FIELDS
        }


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

class NutritionLog(Base):

    __table_args__ = (
        CheckConstraint(
            _non_negative_sql(_NUTRITION_FIELDS), name="nutrition_non_negative",
        ),
        Index("ix_nutrition_logs_user_entry_datetime", "user_id", "entry_datetime"),
    )

    # Optionally tied to a given recipe, for "cooking" meals
    # ondelete:  NutritionLogs don't depend on Recipes in the same way that Transactions do Products
    # recipe_id is simply lineage, so SET NULL should work here
    recipe_id: Mapped[int | None] = mapped_column(ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True)

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

    def __repr__(self) -> str:
        return f"<NutritionLog id={self.id} entry={self.entry_datetime} calories={self.calories} meal={self.meal}"

class InventoryLedgerEventTypeEnum(StrEnum):
    PURCHASE = auto()    # logging a txn
    CONSUMPTION = auto() # logging a meal / NutritionLog
    CORRECTION = auto()  # manual "actually i have 3 of these" override
    WASTE = auto()       # "threw out expired beef"


class InventoryLedger(Base):

    __table_args__ = (
        # Index("ix_inventory_ledger_product_created", "product_id", "created_at"),
        Index("ix_inventory_ledger_user_product_entry", "user_id", "product_id", "entry_datetime"),
        CheckConstraint(
        # Purchase          -> delta must be positive
        # Consumption/Waste -> delta must be negative
        # Corrections must be != 0
            f"(event_type = '{InventoryLedgerEventTypeEnum.PURCHASE}' AND qty_delta > 0) OR "
            f"(event_type IN ('{InventoryLedgerEventTypeEnum.CONSUMPTION}', '{InventoryLedgerEventTypeEnum.WASTE}') AND qty_delta < 0) OR "
            f"(event_type = '{InventoryLedgerEventTypeEnum.CORRECTION}' AND qty_delta != 0)",
            name="ck_inventory_ledger_delta_sign"
        ),
    )

    entry_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # TODO:
    # set null, bc the moment delete_txn tries to delete a txn that has linked ledger rows,
    #    the db would refuse with an FK violation?
    # ondelete="SET NULL" = "when the ref'ed txns row is deleted, set this col to NULL on every
    #   row that pointed at it."
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    # product_id fkey
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped[Product] = relationship(back_populates="ledger_entries", lazy="joined")
    # qty_delta (negative for consumption)
    # This now becomes a Decimal - we're storing qty_delta in master base units
    #  of the given product (either g or ml) (changing net_weight on products later then
    # wouldn't invalidate the ledger values)
    qty_delta: Mapped[Decimal] = mapped_column(Numeric(QTY_PRECISION, QTY_SCALE), nullable=False)
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

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_product_inventory_user_product"),
    )
    # product_id fkkey, unique per user
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False) # unique so each product has ONE inventory record ofc
    product: Mapped[Product] = relationship(back_populates="inventory", lazy="joined") # one-to-one, sqlalchemy infers cardinality from the type annotation: thing vs list[thing]
    # qty_on_hand (current stock ofc)
    # Needs to mirror InventoryLedger's qty_delta being in "200g" form, NOT count
    # So this'll become a Numeric, same at InventoryLedger's qty_delta,
    #  as it is to be a cached SUM(qty_delta)
    qty_on_hand: Mapped[Decimal] = mapped_column(Numeric(QTY_PRECISION, QTY_SCALE), nullable=False)
