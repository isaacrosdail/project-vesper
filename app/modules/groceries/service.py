"""
Service layer for Groceries module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import io

    from sqlalchemy.orm import Session

    from app.modules.groceries.models import (
        Product,
        ShoppingList,
        ShoppingListItem,
        Transaction,
    )

import csv
from datetime import datetime
from zoneinfo import ZoneInfo

import app.shared.datetime_.helpers as dth
from app.modules.groceries.models import (
    MEAL_TIMES,
    NUMERIC_MAPPINGS,
    MealEnum,
    NutritionLog,
    Recipe,
)
from app.modules.groceries.repository import (
    NutritionLogRepository,
    ProductRepository,
    RecipeIngredientRepository,
    RecipeRepository,
    ShoppingListItemRepository,
    ShoppingListRepository,
    ShoppingTripRepository,
    TransactionRepository,
)
from app.modules.groceries.schemas import (
    ProductCreate,
    ProductPatch,
    RecipeCreate,
    RecipePatch,
    ShoppingListItemPatch,
    TransactionCreate,
    TransactionPatch,
)
from app.shared.exceptions import ServiceError


class GroceriesService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        product_repo: ProductRepository,
        transaction_repo: TransactionRepository,
        shopping_list_repo: ShoppingListRepository,
        shopping_list_item_repo: ShoppingListItemRepository,
        recipe_repo: RecipeRepository,
        recipe_ingredient_repo: RecipeIngredientRepository,
        nutrition_log_repo: NutritionLogRepository,
        shopping_trip_repo: ShoppingTripRepository,
    ) -> None:
        self.session = session
        self.product_repo = product_repo
        self.transaction_repo = transaction_repo
        self.shopping_list_repo = shopping_list_repo
        self.shopping_list_item_repo = shopping_list_item_repo
        self.recipe_repo = recipe_repo
        self.recipe_ingredient_repo = recipe_ingredient_repo
        self.nutrition_log_repo = nutrition_log_repo
        self.shopping_trip_repo = shopping_trip_repo
        self.user_tz = user_tz


    def create_product(self, validated: ProductCreate) -> Product:
        product = self.product_repo.create_product(
            barcode=validated.barcode,
            name=validated.name,
            category=validated.category,
            net_weight=validated.net_weight,
            unit_type=validated.unit_type,
            calories_per_100g=validated.calories_per_100g,
        )
        # TODO: Cleanup? sloppy?
        self.session.flush()
        return product

    def update_product(self, validated: ProductPatch, product_id: int) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ServiceError("Product not found", 404)
        for field in validated.model_fields_set:
            setattr(product, field, getattr(validated, field))
        return product


    def update_transaction(self, validated: TransactionPatch, transaction_id: int) -> Transaction:
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise ServiceError("Transaction not found", 404)
        transaction.price_at_scan = validated.price_at_scan
        transaction.quantity = validated.quantity
        return transaction

    def create_transaction(self, data: dict[str, Any]) -> Transaction:
        product_id = data["product_id"]

        # Resolve product id
        if product_id == "__new__":
            validated_product = ProductCreate(**data)
            product = self.create_product(validated_product)
            product_id = product.id
        else:
            product_id = int(product_id)

        validated = TransactionCreate(
            product_id=product_id,
            price_at_scan=data["price_at_scan"],
            quantity=data["quantity"]
        )

        # Increment quantity if existing txn exists for same day at same price
        start_utc, end_utc = dth.today_range_utc(self.user_tz)
        existing_transaction = self.transaction_repo.get_transaction_in_window(
            product_id, start_utc, end_utc
        )

        if existing_transaction and (
            existing_transaction.price_at_scan == validated.price_at_scan
        ):
            existing_transaction.quantity += validated.quantity
            return existing_transaction

        transaction = self.transaction_repo.create_transaction(
            product_id, price_at_scan=validated.price_at_scan, quantity=validated.quantity
        )
        self.session.flush()
        return transaction


    def add_item_to_shopping_list(
        self, product_id: int, quantity_wanted: int = 1
    ) -> ShoppingListItem:
        """Add product to shopping list, incrementing if already exists."""
        shopping_list, _ = self.get_or_create_shopping_list()

        existing_item = self.shopping_list_item_repo.get_shopping_list_item(
            shopping_list.id, product_id
        )

        if existing_item:
            existing_item.quantity_wanted += quantity_wanted
            self.shopping_list_item_repo.session.flush()
            return existing_item

        item = self.shopping_list_item_repo.create_shopping_list_item(
            shopping_list.id, product_id, quantity_wanted
        )
        self.shopping_list_item_repo.session.flush()
        return item

    def update_shopping_list_item(self, item_id: int, validated: ShoppingListItemPatch) -> ShoppingListItem:
        item = self.shopping_list_item_repo.get_by_id(item_id)
        if not item:
            raise ServiceError("Shopping list item not found", 404)
        for field in validated.model_fields_set:
            setattr(item, field, getattr(validated, field))
        return item


    def get_or_create_shopping_list(self) -> tuple[ShoppingList, bool]:
        """Return ShoppingList from database, else create new and return that."""
        shopping_list = self.shopping_list_repo.get_shopping_list()

        if shopping_list:
            return shopping_list, False
        return self.shopping_list_repo.create_shopping_list(), True

    def get_or_create_product(
        self, typed_product_data: dict[str, Any]
    ) -> tuple[Product, bool]:
        """Get existing product or create new one. Returns tuple (product, was_created)."""
        barcode = typed_product_data["barcode"]
        product = self.product_repo.get_product_by_barcode(barcode)
        if product:
            return product, False
        return self.product_repo.create_product(**typed_product_data), True

    def create_recipe(self, validated: RecipeCreate) -> Recipe:
        recipe = self.recipe_repo.create_recipe(validated.name, validated.yields, validated.yields_units)
        self.recipe_repo.session.flush()
        for ingredient in validated.ingredients:
            self.recipe_ingredient_repo.create_recipe_ingredient(
                recipe_id=recipe.id,
                product_id=ingredient.product_id,
                amount_value=ingredient.amount_value,
                amount_units=ingredient.amount_units,
            )
        return recipe

    def update_recipe(self, recipe_id: int, validated: RecipePatch) -> Recipe:
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise ServiceError("Recipe not found", 404)

        for field in validated.model_fields_set:
            if field == "ingredients":
                recipe.ingredients.clear()
                for ing in validated.ingredients:
                    self.recipe_ingredient_repo.create_recipe_ingredient(
                    recipe_id=recipe.id,
                    product_id=ing.product_id,
                    amount_value=ing.amount_value,
                    amount_units=ing.amount_units,
                )
            else:
                setattr(recipe, field, getattr(validated, field))
        return recipe


    def import_nutrition_csv(self, file_stream: io.TextIOWrapper) -> int:
        """Parses incoming nutrition log CSV file stream and bulk inserts. Returns length of persisted entries."""
        reader = csv.DictReader(file_stream)

        # Query all entries to prevent repeats
        existing = {(log.entry_datetime, log.meal) for log in self.nutrition_log_repo.get_all()}
        entries = []
        for row in reader:
            meal_enum = MealEnum.from_label(row["Meal"])
            meal_time = MEAL_TIMES[meal_enum]
            entry_datetime = (
                datetime.strptime(row["Date"], "%Y-%m-%d")
                .replace(hour=meal_time.hour, minute=meal_time.minute, tzinfo=ZoneInfo(self.user_tz))
            )

            # Skip entries we already have - set lookup is O(1)
            if (entry_datetime, meal_enum) in existing:
                continue

            nutrients = {db_col: float(row[csv_col] or 0) for csv_col, db_col in NUMERIC_MAPPINGS.items()}
            entry = NutritionLog(
                entry_datetime=entry_datetime,
                meal=meal_enum,
                user_id=self.nutrition_log_repo.user_id,
                **nutrients
            )
            entries.append(entry)
        self.nutrition_log_repo.session.add_all(entries)
        return len(entries)

    def macros_summary(self, targets: dict[str, str]) -> dict[str, float]:
        # query today's nutrition logs and sum protein/fat/carbs
        start_utc, end_utc = dth.last_n_days_range(days_ago=1, tz_str=self.user_tz) # TODO: change to 1 again
        logs = self.nutrition_log_repo.get_all_in_window(start_utc, end_utc, date_col="entry_datetime")
        fields = ["calories", "protein", "carbs", "fat", "sodium", "potassium"]
        # For each of the fields, get {field}_target from our targets dict, cast to ints
        # TODO: Need to fix this: using 0's will of course bork avg calculations
        targets_dict = {field: int(targets.get(f"{field}_target", 0)) for field in fields}
        result = {}
        for field in fields:
            vals = [getattr(log, field) for log in logs if getattr(log, field)]
            actual = sum(vals)
            target = targets_dict[field]
            result[field] = {
                "actual": round(actual),
                "target": target,
                "pct": round(actual / target * 100) if target else 0,
            }
        meals = {}
        for log in logs:
            meals.setdefault(log.meal, 0)
            meals[log.meal] += log.calories or 0

        return result, meals


def create_groceries_service(
    session: Session, user_id: int, user_tz: str
) -> GroceriesService:
    """Factory function to instantiate GroceriesService with required repositories."""
    return GroceriesService(
        session=session,
        user_tz=user_tz,
        product_repo=ProductRepository(session, user_id),
        transaction_repo=TransactionRepository(session, user_id),
        shopping_list_repo=ShoppingListRepository(session, user_id),
        shopping_list_item_repo=ShoppingListItemRepository(session, user_id),
        recipe_repo=RecipeRepository(session, user_id),
        recipe_ingredient_repo=RecipeIngredientRepository(session, user_id),
        nutrition_log_repo=NutritionLogRepository(session, user_id),
        shopping_trip_repo=ShoppingTripRepository(session, user_id)
    )
