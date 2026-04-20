from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

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


class ProductCreate(BaseModel):
    name: str = Field(max_length=PRODUCT_NAME_MAX_LENGTH)
    category: ProductCategoryEnum
    barcode: str | None = Field(default=None, pattern=BARCODE_REGEX)
    net_weight: float = Field(ge= 0)
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

class ProductPatch(BaseModel):
    name: str | None = Field(default=None, max_length=PRODUCT_NAME_MAX_LENGTH)
    category: ProductCategoryEnum | None = None
    barcode: str | None = Field(default=None, pattern=BARCODE_REGEX)
    net_weight: float | None = Field(default=None, ge=0)
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


class TransactionCreate(BaseModel):
    product_id: int
    price_at_scan: Decimal = Field(gt=0, decimal_places=2)
    quantity: int = Field(gt=0)


class TransactionPatch(BaseModel):
    price_at_scan: Decimal = Field(gt=0, decimal_places=2)
    quantity: int = Field(gt=0)


class ShoppingListCreate(BaseModel):
    name: str = Field(max_length=SHOPPING_LIST_NAME_MAX_LENGTH)


class ShoppingListItemCreate(BaseModel):
    product_id: int
    quantity_wanted: int = Field(gt=0)

class ShoppingListItemPatch(BaseModel):
    quantity_wanted: int | None = Field(default=None, gt=0)
    is_checked: bool | None = None

class RecipeIngredientCreate(BaseModel):
    product_id: int
    amount_value: float = Field(gt=0)
    amount_units: UnitEnum


class RecipeCreate(BaseModel):
    name: str = Field(max_length=RECIPE_NAME_MAX_LENGTH)
    yields: float = Field(gt=0)
    yields_units: UnitEnum
    ingredients: list[RecipeIngredientCreate] = []


class RecipePatch(BaseModel):
    name: str | None = Field(default=None, max_length=RECIPE_NAME_MAX_LENGTH)
    yields: float | None = Field(default=None, gt=0)
    yields_units: UnitEnum | None = None
    ingredients: list[RecipeIngredientCreate] | None = None




class NutritionLogCreate(BaseModel):
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

class InventoryLedgerCreate(BaseModel):
    # product_id: int
    qty_delta: int
    event_type: InventoryLedgerEventTypeEnum
    note: str | None = Field(default=None, max_length=500) # TODO: Make a var

class ProductInventoryCreate(BaseModel):
    qty_on_hand: int = Field(ge=0)
