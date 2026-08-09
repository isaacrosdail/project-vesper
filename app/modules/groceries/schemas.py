from datetime import datetime
from decimal import Decimal
from typing import Literal, Self, cast

from pydantic import Field, model_validator

from app.modules.groceries.models import (
    BARCODE_REGEX,
    PRODUCT_NAME_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    SHOPPING_LIST_NAME_MAX_LENGTH,
    InventoryLedgerEventTypeEnum,
    MealEnum,
    ProductCategoryEnum,
    UnitEnum,
)
from app.shared.schemas import APIReadSchema, APISchema, TargetRead
from app.shared.target import TargetStatus


class ProductCreate(APISchema):
    name: str = Field(max_length=PRODUCT_NAME_MAX_LENGTH)
    category: ProductCategoryEnum
    barcode: str | None = Field(default=None, pattern=BARCODE_REGEX)
    net_weight: Decimal = Field(gt=0)
    unit_type: UnitEnum
    calories_per_100g: float | None = Field(default=None, ge=0)
    protein_per_100g: float | None = Field(default=None, ge=0)
    fat_per_100g: float | None = Field(default=None, ge=0)
    fat_mono_per_100g: float | None = Field(default=None, ge=0)
    fat_poly_per_100g: float | None = Field(default=None, ge=0)
    fat_sat_per_100g: float | None = Field(default=None, ge=0)
    carbs_per_100g: float | None = Field(default=None, ge=0)
    carbs_fiber_per_100g: float | None = Field(default=None, ge=0)
    carbs_sugar_per_100g: float | None = Field(default=None, ge=0)
    sodium_per_100g: float | None = Field(default=None, ge=0)
    potassium_per_100g: float | None = Field(default=None, ge=0)

    @model_validator(mode='after')
    def validate_nutrition(self) -> Self:
        # Macro subtypes can't exceed their parent
        if self.fat_per_100g is not None:
            sub_fat = sum(filter(None, [self.fat_mono_per_100g, self.fat_poly_per_100g, self.fat_sat_per_100g]))
            if sub_fat > self.fat_per_100g:
                raise ValueError(f'Fat subtypes ({sub_fat}g) exceed total fat ({self.fat_per_100g})')

        if self.carbs_per_100g is not None:
            sub_carbs = sum(filter(None, [self.carbs_fiber_per_100g, self.carbs_sugar_per_100g]))
            if sub_carbs > self.carbs_per_100g:
                raise ValueError(f'Carb subtypes ({sub_carbs}g) exceed total carbs ({self.carbs_per_100g})')

        # Calories sanity check
        if all(v is not None for v in [self.protein_per_100g, self.fat_per_100g, self.carbs_per_100g, self.calories_per_100g]):
            computed = (self.protein_per_100g * 4) + (self.carbs_per_100g * 4) + (self.fat_per_100g * 9)
            if abs(computed - self.calories_per_100g) > self.calories_per_100g * 0.15:
                raise ValueError(f'Calories ({self.calories_per_100g}) inconsistent with macros (computed: {computed:.0f})')

        return self

class ProductPatch(APISchema):
    name: str | None = Field(default=None, max_length=PRODUCT_NAME_MAX_LENGTH)
    category: ProductCategoryEnum | None = None
    barcode: str | None = Field(default=None, pattern=BARCODE_REGEX)
    net_weight: Decimal | None = Field(default=None, gt=0)
    unit_type: UnitEnum | None = None
    calories_per_100g: float | None = Field(default=None, ge=0)
    protein_per_100g: float | None = Field(default=None, ge=0)
    fat_per_100g: float | None = Field(default=None, ge=0)
    fat_mono_per_100g: float | None = Field(default=None, ge=0)
    fat_poly_per_100g: float | None = Field(default=None, ge=0)
    fat_sat_per_100g: float | None = Field(default=None, ge=0)
    carbs_per_100g: float | None = Field(default=None, ge=0)
    carbs_fiber_per_100g: float | None = Field(default=None, ge=0)
    carbs_sugar_per_100g: float | None = Field(default=None, ge=0)
    sodium_per_100g: float | None = Field(default=None, ge=0)
    potassium_per_100g: float | None = Field(default=None, ge=0)


class ProductRead(APIReadSchema):
    id: int
    name: str
    category: ProductCategoryEnum
    barcode: str | None
    net_weight: float
    unit_type: UnitEnum
    calories_per_100g: float | None
    protein_per_100g: float | None
    fat_per_100g: float | None
    carbs_per_100g: float | None
    fat_mono_per_100g: float | None
    fat_poly_per_100g: float | None
    fat_sat_per_100g: float | None
    carbs_fiber_per_100g: float | None
    carbs_sugar_per_100g: float | None
    sodium_per_100g: float | None
    potassium_per_100g: float | None
    created_at: datetime
    subtype: Literal['products']

### TODO: gonna be a bit messier to implement route-side
class TransactionCreate(APISchema):
    product_id: int | None = None
    product: ProductCreate | None = None
    price_at_scan: Decimal = Field(gt=0, decimal_places=2)
    quantity: int = Field(gt=0)

    @model_validator(mode="after")
    def exactly_one_product_source(self) -> Self:
        if (self.product_id is None) == (self.product is None):
            raise ValueError("Provide exactly one of product_id or product")
        return self


class TransactionPatch(APISchema):
    price_at_scan: Decimal | None = Field(None, gt=0, decimal_places=2)
    quantity: int | None = Field(None, gt=0)


class TransactionRead(APIReadSchema):
    id: int
    product_id: int
    product_name: str | None
    shopping_trip_id: int | None
    price_at_scan: float
    quantity: int
    price_per_100g: float
    net_weight: float
    unit_type: UnitEnum
    created_at: datetime
    subtype: Literal['transactions']


class ShoppingListCreate(APISchema):
    name: str = Field(max_length=SHOPPING_LIST_NAME_MAX_LENGTH)


class ShoppingListItemCreate(APISchema):
    product_id: int
    quantity_wanted: int = Field(gt=0)

class ShoppingListItemPatch(APISchema):
    quantity_wanted: int | None = Field(default=None, gt=0)
    is_checked: bool | None = None

class ShoppingListItemRead(APIReadSchema):
    id: int
    shopping_list_id: int
    product_id: int
    product_name: str | None
    quantity_wanted: int
    is_checked: bool
    net_weight: float
    unit_type: UnitEnum
    created_at: datetime
    subtype: Literal['shopping_list_items']


class RecipeIngredientCreate(APISchema):
    product_id: int
    amount_value: Decimal = Field(gt=0)
    amount_units: UnitEnum

class RecipeIngredientRead(APIReadSchema):
    product_id: int
    product_name: str | None
    amount_value: float
    amount_units: UnitEnum


class RecipeCreate(APISchema):
    name: str = Field(max_length=RECIPE_NAME_MAX_LENGTH)
    yields: Decimal = Field(gt=0)
    yields_units: UnitEnum
    ingredients: list[RecipeIngredientCreate] = []


class RecipePatch(APISchema):
    name: str | None = Field(default=None, max_length=RECIPE_NAME_MAX_LENGTH)
    yields: Decimal | None = Field(default=None, gt=0)
    yields_units: UnitEnum | None = None
    ingredients: list[RecipeIngredientCreate] | None = None

class RecipeRead(APIReadSchema):
    id: int
    name: str
    yields: float
    yields_units: UnitEnum
    ingredients: list[RecipeIngredientRead]
    created_at: datetime
    subtype: Literal['recipes']


class NutritionLogCreate(APISchema):
    entry_datetime: datetime
    meal: MealEnum
    calories: float | None = Field(default=None, ge=0)
    protein: float | None = Field(default=None, ge=0)
    fat: float | None = Field(default=None, ge=0)
    carbs: float | None = Field(default=None, ge=0)
    fat_mono: float | None = Field(default=None, ge=0)
    fat_poly: float | None = Field(default=None, ge=0)
    fat_sat: float | None = Field(default=None, ge=0)
    carbs_fiber: float | None = Field(default=None, ge=0)
    carbs_sugar: float | None = Field(default=None, ge=0)

    sodium: float | None = Field(default=None, ge=0)
    potassium: float | None = Field(default=None, ge=0)

class LogProductRequest(APISchema):
    product_id: int
    grams: Decimal = Field(gt=0)
    meal: MealEnum
    entry_datetime: datetime

class InventoryLedgerCreate(APISchema):
    # product_id: int
    qty_delta: int
    event_type: InventoryLedgerEventTypeEnum
    note: str | None = Field(default=None, max_length=500) # TODO: Make a var

class ProductInventoryCreate(APISchema):
    qty_on_hand: int = Field(ge=0)


class CookRequest(APISchema):
    meal: MealEnum
    entry_datetime: datetime


class ShortfallRead(APIReadSchema):
    product_id: int
    product_name: str
    deficit_value: float  # Decimal on the dataclass; float here so JSON gets a number, not a string
    unit: UnitEnum

class RecipeSlotRead(APIReadSchema):
    id: int
    name: str
    yields: float | None
    yields_units: UnitEnum | None
    missing: list[ShortfallRead]


class MacroLineRead(APIReadSchema):
    actual: int
    target: TargetRead | None
    pct: int | None
    target_status: TargetStatus | None

class MacrosSummaryRead(APIReadSchema):
    calories: MacroLineRead
    protein: MacroLineRead
    carbs: MacroLineRead
    fat: MacroLineRead
    sodium: MacroLineRead
    potassium: MacroLineRead

