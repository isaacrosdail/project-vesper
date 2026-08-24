"""
Service layer for Groceries module.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any, TypedDict

from sqlalchemy import select

from app.modules.auth.models import User
from app.shared.target import Target, TargetStatus

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
    InventoryLedger,
    InventoryLedgerEventTypeEnum,
    MealEnum,
    NutritionLog,
    ProductCategoryEnum,
    ProductInventory,
    Recipe,
    RecipeIngredient,
    ShoppingTrip,
    UnitEnum,
)
from app.modules.groceries.repository import (
    InventoryLedgerRepository,
    NutritionLogRepository,
    ProductInventoryRepository,
    ProductRepository,
    RecipeIngredientRepository,
    RecipeRepository,
    ShoppingListItemRepository,
    ShoppingListRepository,
    ShoppingTripRepository,
    TransactionRepository,
)
from app.modules.groceries.schemas import (
    GroceriesDashboardPayload,
    ProductCreate,
    ProductPatch,
    RecipeCreate,
    RecipePatch,
    ShoppingListItemPatch,
    ShoppingTripCreate,
    TransactionCreate,
    TransactionPatch,
)
from app.shared.exceptions import ServiceError


class GroceriesService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        user_id: int,
        product_repo: ProductRepository,
        transaction_repo: TransactionRepository,
        shopping_list_repo: ShoppingListRepository,
        shopping_list_item_repo: ShoppingListItemRepository,
        recipe_repo: RecipeRepository,
        recipe_ingredient_repo: RecipeIngredientRepository,
        nutrition_log_repo: NutritionLogRepository,
        shopping_trip_repo: ShoppingTripRepository,
        product_inventory_repo: ProductInventoryRepository,
        inventory_ledger_repo: InventoryLedgerRepository,
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
        self.product_inventory_repo = product_inventory_repo
        self.inventory_ledger_repo = inventory_ledger_repo
        self.user_id = user_id
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
    
    def delete_product(self, product_id: int) -> Product:
        """Soft-deletes a Product and removes its ShoppingListItem rows."""
        product = self.product_repo.get_active_by_id(product_id)
        if product is None:
            raise ServiceError("Error: product not found", 404)
        # purge product's shoppinglistitem rows
        self.shopping_list_item_repo.delete_by_product_id(product_id)

        product.deleted_at = dth.now_utc()
        return product
    
    def get_product(self, product_id: int) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if product is None:
            raise ServiceError("Product not found", 404)
        return product
    
    def get_transaction(self, transaction_id: int) -> Transaction:
        txn = self.transaction_repo.get_by_id(transaction_id)
        if txn is None:
            raise ServiceError("Transaction not found", 404)
        return txn

    def update_transaction(self, validated: TransactionPatch, transaction_id: int) -> Transaction:
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise ServiceError("Transaction not found", 404)
        if validated.price_at_scan is not None:
            transaction.price_at_scan = validated.price_at_scan
        old_quantity = transaction.quantity
        # qty_delta rejects deltas of 0 - guard:

        if validated.quantity is not None and old_quantity != validated.quantity:
            per_unit = self.inventory_ledger_repo.sum_deltas_for_transaction(transaction.id) / old_quantity
            qty_delta = (validated.quantity - old_quantity) * per_unit
            self._record_inventory_event(transaction.product.id, qty_delta, event_type=InventoryLedgerEventTypeEnum.CORRECTION,
                entry_datetime=dth.now_utc(), transaction_id=transaction.id)
            transaction.quantity = validated.quantity
        return transaction

    def create_transaction(self, validated: TransactionCreate) -> Transaction:
        # product_id = data["product_id"]
        if validated.product is not None:
            product = self.create_product(validated.product)
        else:
            product = self.product_repo.get_by_id(validated.product_id)
            if product is None:
                raise ServiceError("Product not found", 404)

        # Increment quantity if existing txn exists for same day at same price
        start_utc, end_utc = dth.today_range_utc(self.user_tz)
        existing_transaction = self.transaction_repo.get_transaction_in_window(
            product.id, start_utc, end_utc
        )

        if existing_transaction and (
            existing_transaction.price_at_scan == validated.price_at_scan
        ):
            existing_transaction.quantity += validated.quantity
            transaction = existing_transaction
        else:
            transaction = self.transaction_repo.create_transaction(
                product.id, price_at_scan=validated.price_at_scan, quantity=validated.quantity
            )
        self.session.flush() # transaction.id must exist before the ledger link

        qty_delta = validated.quantity * product.net_weight * product.unit_type.factor
        self._record_inventory_event(product.id, qty_delta, event_type=InventoryLedgerEventTypeEnum.PURCHASE,
            entry_datetime=dth.now_utc(), transaction_id=transaction.id)
        return transaction

    def delete_transaction(self, transaction_id: int) -> Transaction:
        txn = self.transaction_repo.get_by_id(transaction_id)
        if txn is None:
            raise ServiceError("Transaction not found", 404)
        # Ledger correction prior to deleting transaction
        qty_delta = -1 * self.inventory_ledger_repo.sum_deltas_for_transaction(txn.id)
        self._record_inventory_event(txn.product.id, qty_delta, event_type=InventoryLedgerEventTypeEnum.CORRECTION,
            entry_datetime=dth.now_utc(), transaction_id=txn.id)
        self.transaction_repo.delete(txn)
        return txn


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

    def delete_shopping_list_item(self, item_id: int) -> ShoppingListItem:
        item = self.shopping_list_item_repo.get_by_id(item_id)
        if not item:
            raise ServiceError("Shopping list item not found", 404)
        self.shopping_list_item_repo.delete(item)
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

    def _validate_ingredients(self, ingredients: list[RecipeIngredient]) -> None:
        products = self.product_repo.get_by_ids([i.product_id for i in ingredients])
        products_by_id = {p.id: p for p in products}
        for ing in ingredients:
            product = products_by_id.get(ing.product_id)
            if product is None:
                raise ServiceError(f"unknown product id {ing.product_id}")
            if product.unit_type.dimension != ing.amount_units.dimension:
                raise ServiceError(f"ingredient {product.name}: {ing.amount_units} is {ing.amount_units.dimension}, product is {product.unit_type.dimension}")

    def create_recipe(self, validated: RecipeCreate) -> Recipe:
        self._validate_ingredients(validated.ingredients)
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

        if "ingredients" in validated.model_fields_set:
            self._validate_ingredients(validated.ingredients)

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

    def delete_recipe(self, recipe_id: int) -> Recipe:
        """Deletes Recipe. Eager-loads with ingredients, as those cascade delete."""
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ServiceError("Recipe not found", 404)
        self.recipe_repo.delete(recipe)
        return recipe

    def create_shopping_trip(self, validated: ShoppingTripCreate) -> ShoppingTrip:
        txns = [
            self.create_transaction(TransactionCreate(
                product_id=line.product_id,
                price_at_scan=line.price_at_scan,
                quantity=line.quantity,
            ))
            for line in validated.lines
        ]
        trip = self.shopping_trip_repo.create_shopping_trip(
            store_name=validated.store_name,
            entry_datetime=validated.entry_datetime,
            total_price=sum(l.price_at_scan * l.quantity for l in validated.lines),
        )
        for txn in txns:
            txn.shopping_trip = trip
        return trip


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

    def macros_summary(self, start_utc: datetime, end_utc: datetime) -> tuple[dict[str, MacroLine], dict[MealEnum, int]]:
        logs = self.nutrition_log_repo.get_all_in_window(start_utc, end_utc, date_col=NutritionLog.entry_datetime)
        logged_days = len({dth.convert_to_timezone(self.user_tz, log.entry_datetime).date() for log in logs})

        user = self.session.execute(select(User).where(User.id==self.user_id)).scalar_one() # TODO(jank): fix

        targets_dict: dict[str, Target | None] = {
            f: MACRO_POLICIES[f](v) if (v := getattr(user.goals, f)) is not None else None
            for f in MACRO_POLICIES
        }
        result = summarize_macros(logs, targets_dict, logged_days=logged_days)
        cals_by_meal = calories_by_meal(logs)
        return result, cals_by_meal

    def groceries_dashboard(self, start_utc: datetime, end_utc: datetime) -> dict[str, Any]:
        logs = self.nutrition_log_repo.get_all_in_window(start_utc, end_utc, date_col=NutritionLog.entry_datetime)
        txns = self.transaction_repo.get_all_in_window(start_utc, end_utc)

        num_transactions = len(txns)
        num_products = len({t.product_id for t in txns})
        num_trips = self.shopping_trip_repo.count_in_window(start_utc, end_utc, date_col=ShoppingTrip.entry_datetime)

        top_products = self.transaction_repo.get_top_purchased_products(start_utc, end_utc, limit=5)
        macros_targets, cals_by_meal = self.macros_summary(start_utc, end_utc)
        num_meals_logged = len(logs)
        cals_by_day: dict[date, int] = {}
        for log in logs:
            day = dth.convert_to_timezone(self.user_tz, log.entry_datetime).date()
            cals_by_day[day] = cals_by_day.get(day, 0) + int(log.calories or 0)

        # For spend per-category breakdowns:
        spend_by_category: dict[ProductCategoryEnum, Decimal] = {}
        for t in txns:
            spend_by_category[t.product.category] = spend_by_category.get(t.product.category, 0) + t.price_at_scan * t.quantity

        class CategorySpend(TypedDict):
            category: ProductCategoryEnum
            spent: Decimal
            pct: int

        category_spends: list[CategorySpend] = []
        total_spend = sum(spend_by_category.values())
        for category, spent in spend_by_category.items():
            new_entry: CategorySpend = {
                "category": category,
                "spent": spent,
                "pct": round(spent / total_spend * 100) if total_spend else 0,
            }
            category_spends.append(new_entry)
        # Sort desc by spent
        category_spends.sort(key=lambda r: r["spent"], reverse=True)

        avg_daily_cals = macros_targets["calories"]["actual"] or 0
        if (target := macros_targets["calories"]["target"]) is None:
            status = None
            days_on_target = None
        else:
            days_on_target = sum(1 for v in cals_by_day.values() if target.satisfied(v))
            status = target.status(avg_daily_cals)

        last_shopping_trip = self.shopping_trip_repo.get_most_recent_trip()

        top_five_recipes_cooked = [
            {"id": rid, "name": name, "count": n}
            for rid, name, n in self.nutrition_log_repo.get_top_cooked_recipes(start_utc, end_utc)
        ]

        shopping_list_items = self.shopping_list_item_repo.get_all()

        return {
            "intake": {
                "targets": macros_targets,
                "cals_avg_daily": avg_daily_cals,
                "days_on_target": days_on_target,
                "total_cals_over_period": sum(cals_by_day.values()),
                "num_meals_logged": num_meals_logged,
                "days_logged": len(cals_by_day),
                "status": status,
                "meals_today": cals_by_meal,
            },
            "purchase_insights": {
                "top_products": top_products,
                "num_transactions": num_transactions,
                "num_products": num_products,
                "total_spent": total_spend,
                "num_trips": num_trips,
                "last_shopping_trip": last_shopping_trip,
            },
            "midsection": {
                "num_meals_logged": num_meals_logged,
                "top_five_recipes_cooked": top_five_recipes_cooked,
                "total_spent": total_spend,
                # Per-macro OR per-category breakdowns
                "category_spends": category_spends,
                "shopping_list_items": shopping_list_items,
            },
        }

    def cook_recipe(self, recipe_id: int, meal: MealEnum, entry_datetime: datetime) -> None:
        """Logs a cooked recipe as one NutritionLog and consumes its ingredients.
        
        Raises 409 if stock is short: recipes are all-or-nothing.
        """
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise ServiceError(f"recipe id {recipe_id} not found", 404)

        shortfalls = compute_shortfalls(
            recipe.ingredients, self.product_inventory_repo.get_qty_map()
        )
        if shortfalls:
            raise ServiceError("Not enough ingredients", 409)

        totals: dict[str, Decimal] = {}
        for ing in recipe.ingredients:
            for macro, val in ing.nutrition_contribution.items():
                totals[macro] = totals.get(macro, Decimal(0)) + val

        entry = NutritionLog(
            user_id=self.user_id,
            recipe_id=recipe_id,
            entry_datetime=entry_datetime,
            meal=meal,
            **totals
        )
        self.session.add(entry)

        for ing in recipe.ingredients:
            self._record_inventory_event(
                ing.product_id, -ing.grams,
                InventoryLedgerEventTypeEnum.CONSUMPTION, entry_datetime
            )

    def log_product_consumption(self, product_id: int, grams: Decimal, meal: MealEnum, entry_datetime: datetime) -> None:
        product = self.product_repo.get_active_by_id(product_id)
        if not product:
            raise ServiceError(f"product id {product_id} not found")

        nutritionlog_entry = NutritionLog(
            user_id=self.user_id,
            recipe_id=None,
            entry_datetime=entry_datetime,
            meal=meal,
            **product.nutrition_for(grams)
        )
        self.session.add(nutritionlog_entry)
        self._record_inventory_event(
            product_id, -grams, InventoryLedgerEventTypeEnum.CONSUMPTION, entry_datetime
        )


    def get_recipes_with_shortfalls(self) -> list[tuple[Recipe, list[IngredientShortfall]]]:
        """Pairs each recipe with what's missing from inventory, sorted ready-first.

        Readiness is determined per recipe against current stock: two ready recipes sharing
        an ingredient do not reserve it from each other.
        """
        recipes = self.recipe_repo.get_all()
        qty_map = self.product_inventory_repo.get_qty_map()

        pairs = [(r, compute_shortfalls(r.ingredients, qty_map)) for r in recipes]
        pairs.sort(key=lambda pair: len(pair[1]))
        return pairs

    def add_recipe_shortfalls_to_list(self, recipe_id: int) -> list[ShoppingListItem]:
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ServiceError("Recipe not found", 404)
        qty_map = self.product_inventory_repo.get_qty_map()
        shortfalls = compute_shortfalls(recipe.ingredients, qty_map)
        return [
            self.add_item_to_shopping_list(sf.product_id, sf.packages_needed)
            for sf in shortfalls
        ]

    def _record_inventory_event(
        self, product_id: int, qty_delta: Decimal,
        event_type: InventoryLedgerEventTypeEnum, entry_datetime: datetime, transaction_id: int | None = None
    ) -> None:
        """Helper to record inventory event for any given event."""
        # Guard: Price-only txn edits, deleting txns which pre-date the addition of the ledger, &
        #  stock corrections which match what we already have.
        if qty_delta == 0:
            return
        self.session.add(InventoryLedger(
            user_id=self.user_id, product_id=product_id,
            event_type=event_type, qty_delta=qty_delta, entry_datetime=entry_datetime,
            transaction_id=transaction_id
        ))
        stock = self.product_inventory_repo.get_by_product_id(product_id)
        if stock:
            stock.qty_on_hand += qty_delta
        else:
            self.session.add(ProductInventory(
                user_id=self.user_id, product_id=product_id, qty_on_hand=qty_delta
            ))

def compute_shortfalls(ingredients: Iterable[RecipeIngredient], qty_map: dict[int, Decimal]) -> list[IngredientShortfall]:
    """Compares recipe requirements against stock.
    
    All math is done in base units (g for mass, ml for volume) to match ProductInventory.qty_on_hand.
    Only IngredientShortfall.deficit_value is converted back to the recipe's own units, for display.
    """
    shortfalls = []
    for ing in ingredients:
        amount_on_hand = qty_map.get(ing.product_id, Decimal(0))
        needed = ing.grams
        if needed > amount_on_hand:
            deficit = needed - amount_on_hand
            package_grams = ing.product.net_weight * ing.product.unit_type.factor
            shortfalls.append(IngredientShortfall(
                product_id=ing.product_id,
                product_name=ing.product.name,
                deficit_value=deficit / ing.amount_units.factor,
                unit=ing.amount_units,
                packages_needed=math.ceil(deficit / package_grams)
            ))
    return shortfalls

@dataclass(frozen=True, slots=True)
class IngredientShortfall:
    product_id: int
    product_name: str
    deficit_value: Decimal
    unit: UnitEnum
    packages_needed: int  # for ShoppingListItem.quantity_wanted


## TODO(service): Clean this system/pipeline up
class MacroLine(TypedDict):
    actual: int
    target: Target | None
    pct: int | None
    target_status: TargetStatus | None

MACRO_POLICIES: dict[str, Callable[[int], Target]] = {
    "calories": lambda t: Target.within(value=t, tolerance=0.2 * t),
    "protein": lambda t: Target.at_least(t),
    "carbs": lambda t: Target.at_most(t),
    "fat": lambda t: Target.at_most(t),
    "sodium": lambda t: Target.at_most(t),
    "potassium": lambda t: Target.at_least(t),
}

def summarize_macros(
    logs: list[NutritionLog],
    targets_dict: dict[str, Target | None],
    logged_days: int
) -> dict[str, MacroLine]:
    """Actual values are per-logged-day averages. logged_days is computed by caller (distinct local dates)."""
    result: dict[str, MacroLine] = {}
    for field, target in targets_dict.items():
        vals = [getattr(log, field) or 0 for log in logs]
        actual = sum(vals)
        avg_over_window = actual / logged_days if logged_days else 0
        if target is None:
            pct, status = None, None
        else:
            pct = round(avg_over_window / target.nominal * 100) if target.nominal else 0
            status = target.status(avg_over_window)
        result[field] = {
            "actual": round(avg_over_window),
            "target": target,
            "pct": pct,
            "target_status": status,
        }
    return result


## TODO: this belongs in ORM-land
def calories_by_meal(logs: list[NutritionLog]) -> dict[MealEnum, int]:
    meals: Counter[MealEnum] = Counter()
    for log in logs:
        meals[log.meal] += int(log.calories or 0)
    return meals


def create_groceries_service(
    session: Session, user_id: int, user_tz: str
) -> GroceriesService:
    """Factory function to instantiate GroceriesService with required repositories."""
    return GroceriesService(
        session=session,
        user_tz=user_tz,
        user_id=user_id,
        product_repo=ProductRepository(session, user_id),
        transaction_repo=TransactionRepository(session, user_id),
        shopping_list_repo=ShoppingListRepository(session, user_id),
        shopping_list_item_repo=ShoppingListItemRepository(session, user_id),
        recipe_repo=RecipeRepository(session, user_id),
        recipe_ingredient_repo=RecipeIngredientRepository(session, user_id),
        nutrition_log_repo=NutritionLogRepository(session, user_id),
        shopping_trip_repo=ShoppingTripRepository(session, user_id),
        product_inventory_repo=ProductInventoryRepository(session, user_id),
        inventory_ledger_repo=InventoryLedgerRepository(session, user_id),
    )
