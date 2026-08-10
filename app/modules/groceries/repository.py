"""
Repository layer for groceries module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from decimal import Decimal

    from sqlalchemy.orm import Session

from sqlalchemy import Date, cast, delete, func, select
from sqlalchemy.orm import selectinload

from app.modules.groceries.models import (
    InventoryLedger,
    InventoryLedgerEventTypeEnum,
    NutritionLog,
    Product,
    ProductCategoryEnum,
    ProductInventory,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    ShoppingListItem,
    ShoppingTrip,
    Transaction,
    UnitEnum,
)
from app.shared.repository.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Product)

    def create_product(
        self,
        name: str,
        category: ProductCategoryEnum,
        net_weight: Decimal,
        unit_type: UnitEnum,
        barcode: str | None,
        calories_per_100g: float | None,
    ) -> Product:
        product = Product(
            user_id=self.user_id,
            barcode=barcode,
            name=name,
            category=category,
            net_weight=net_weight,
            unit_type=unit_type,
            calories_per_100g=calories_per_100g,
        )
        return self.add(product)

    def get_all_products(self, *, include_soft_deleted: bool = False) -> list[Product]:
        stmt = self._user_select(Product)
        if not include_soft_deleted:
            stmt = stmt.where(Product.deleted_at.is_(None))
        return list(self.session.scalars(stmt).all())

    def get_all_products_in_window(
        self,
        start_utc: datetime,
        end_utc: datetime,
        *,
        include_soft_deleted: bool = False,
    ) -> list[Product]:
        stmt = self._user_select(Product).where(
            Product.created_at >= start_utc,
            Product.created_at < end_utc,
        )
        if not include_soft_deleted:
            stmt = stmt.where(Product.deleted_at.is_(None))
        return list(self.session.scalars(stmt).all())
    
    # Predicate to filter soft-deleted Products in queries
    def _active(self):
        return self._user_select(Product).where(Product.deleted_at.is_(None))
    
    def get_active_by_id(self, product_id: int) -> Product | None:
        return self.session.execute(
            self._active().where(Product.id == product_id)
        ).scalar_one_or_none()

    def get_product_by_barcode(self, barcode: str) -> Product | None:
        stmt = self._user_select(Product).where(
            Product.barcode == barcode, Product.deleted_at.is_(None)
        )
        return self.session.scalars(stmt).first()

    def get_product_by_name(self, name: str) -> Product | None:
        stmt = self._user_select(Product).where(
            Product.name == name, Product.deleted_at.is_(None)
        )
        return self.session.scalars(stmt).first()


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Transaction)

    def create_transaction(
        self, product_id: int, price_at_scan: Decimal, quantity: int
    ) -> Transaction:
        transaction = Transaction(
            user_id=self.user_id,
            product_id=product_id,
            price_at_scan=price_at_scan,
            quantity=quantity,
        )
        return self.add(transaction)

    def get_top_purchased_products(self, start_utc: datetime, end_utc: datetime, limit: int = 5) -> list[tuple[str, int]]:
        stmt = (
            select(Product.name, func.sum(Transaction.quantity).label("total"))
            .join(Product)
            .where(
                Transaction.user_id == self.user_id,
                Transaction.created_at >= start_utc,
                Transaction.created_at < end_utc,
            )
            .group_by(Product.name)
            .order_by(func.sum(Transaction.quantity).desc())
            .limit(limit)
        )
        rows = self.session.execute(stmt).all()
        return [(name, int(total)) for name, total in rows]


    def get_transaction_in_window(
        self, product_id: int, start_utc: datetime, end_utc: datetime
    ) -> Transaction | None:
        """Get a transaction within a certain datetime window (UTC)."""
        stmt = self._user_select(Transaction).where(
            Transaction.product_id == product_id,
            Transaction.created_at >= start_utc,
            Transaction.created_at < end_utc,
        )
        return self.session.scalars(stmt).first()


class ShoppingListRepository(BaseRepository[ShoppingList]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=ShoppingList)

    def create_shopping_list(self) -> ShoppingList:
        shopping_list = ShoppingList(user_id=self.user_id)
        return self.add(shopping_list)

    def get_shopping_list(self) -> ShoppingList | None:
        """Get shopping list for user. One list per user."""
        stmt = (
            self._user_select(ShoppingList)
            .options(selectinload(ShoppingList.items)
            .joinedload(ShoppingListItem.product))
        )
        return self.session.scalars(stmt).one_or_none()


class ShoppingListItemRepository(BaseRepository[ShoppingListItem]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=ShoppingListItem)

    def create_shopping_list_item(
        self, shopping_list_id: int, product_id: int, quantity_wanted: int
    ) -> ShoppingListItem:
        shopping_list_item = ShoppingListItem(
            user_id=self.user_id,
            shopping_list_id=shopping_list_id,
            product_id=product_id,
            quantity_wanted=quantity_wanted,
        )
        return self.add(shopping_list_item)

    def get_shopping_list_item(
        self, shopping_list_id: int, product_id: int
    ) -> ShoppingListItem | None:
        stmt = self._user_select(ShoppingListItem).where(
            ShoppingListItem.shopping_list_id == shopping_list_id,
            ShoppingListItem.product_id == product_id,
        )
        return self.session.scalars(stmt).one_or_none()
    
    def delete_by_product_id(self, product_id: int) -> None:
        stmt = delete(ShoppingListItem).where(
            ShoppingListItem.user_id == self.user_id,
            ShoppingListItem.product_id == product_id
        )
        self.session.execute(stmt)

class RecipeRepository(BaseRepository[Recipe]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Recipe)

    def create_recipe(
            self, name: str, yields: float, yields_units: UnitEnum
    ) -> Recipe:
        recipe = Recipe(
            user_id=self.user_id,
            name=name,
            yields=yields,
            yields_units=yields_units
        )

        return self.add(recipe)


class RecipeIngredientRepository(BaseRepository[RecipeIngredient]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=RecipeIngredient)

    def create_recipe_ingredient(
            self, recipe_id: int, product_id: int, amount_value: float, amount_units: UnitEnum
    ) -> RecipeIngredient:
        recipe_ingredient = RecipeIngredient(
            user_id=self.user_id,
            recipe_id=recipe_id,
            product_id=product_id,
            amount_value=amount_value,
            amount_units=amount_units
        )

        return self.add(recipe_ingredient)

class NutritionLogRepository(BaseRepository[NutritionLog]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=NutritionLog)

    def get_daily_calorie_totals(self, start_utc: datetime, end_utc: datetime) -> list[dict]:
        stmt = (
            select(
                cast(NutritionLog.entry_datetime, Date).label("date"),
                func.sum(NutritionLog.calories).label("total")
            )
            .where(
                NutritionLog.user_id == self.user_id,
                NutritionLog.entry_datetime >= start_utc,
                NutritionLog.entry_datetime < end_utc,
            )
            .group_by(cast(NutritionLog.entry_datetime, Date))
            .order_by(cast(NutritionLog.entry_datetime, Date))
        )
        results = self.session.execute(stmt).all()
        return [{"date": row.date.isoformat(), "value": row.total} for row in results]

    def get_top_cooked_recipes(
        self, start_utc: datetime, end_utc: datetime, limit: int = 5,
    ) -> list[tuple[int, str, int]]:
        stmt = (
            select(Recipe.id, Recipe.name, func.count().label("times"))
            .select_from(NutritionLog)
            .join(Recipe, Recipe.id == NutritionLog.recipe_id)
            .where(
                NutritionLog.user_id == self.user_id,
                NutritionLog.entry_datetime >= start_utc,
                NutritionLog.entry_datetime < end_utc,
            )
            .group_by(Recipe.id, Recipe.name)
            .order_by(func.count().desc(), Recipe.name)
            .limit(limit)
        )
        return [
            (rid, name, int(times))
            for rid, name, times in self.session.execute(stmt).all()
        ]

class ShoppingTripRepository(BaseRepository[ShoppingTrip]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=ShoppingTrip)

    def get_most_recent_trip(self) -> ShoppingTrip | None:
        stmt = (
            self._user_select(ShoppingTrip)
            .options(selectinload(ShoppingTrip.transactions))
            .order_by(ShoppingTrip.entry_datetime.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

class ProductInventoryRepository(BaseRepository[ProductInventory]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=ProductInventory)

    def get_by_product_id(self, product_id: int) -> ProductInventory | None:
        stmt = self._user_select(ProductInventory).where(
            ProductInventory.product_id == product_id,
        )
        return self.session.scalars(stmt).one_or_none()

    def get_qty_map(self) -> dict[int, Decimal]:
        stmt = select(
            ProductInventory.product_id, ProductInventory.qty_on_hand
        ).where(ProductInventory.user_id == self.user_id)
        return dict(self.session.execute(stmt).all())
    

class InventoryLedgerRepository():
    def __init__(self, session: Session, user_id: int) -> None:
        self.session = session
        self.user_id = user_id

    def get_sum_deltas_for_product(self, product_id: int) -> Decimal:
        stmt = select(func.coalesce(func.sum(InventoryLedger.qty_delta), 0)).where(
            InventoryLedger.user_id == self.user_id,
            InventoryLedger.product_id == product_id,
        )
        return self.session.scalar(stmt)
    
    def sum_deltas_for_transaction(self, transaction_id: int) -> Decimal:
        stmt = select(func.coalesce(func.sum(InventoryLedger.qty_delta), 0)).where(
            InventoryLedger.user_id == self.user_id,
            InventoryLedger.transaction_id == transaction_id,
        )
        return self.session.scalar(stmt)

    def append(self, entry: InventoryLedger) -> InventoryLedger:
        self.session.add(entry)
        return entry

    def get_all_for_product(self, product_id: int) -> list[InventoryLedger]:
        stmt = select(InventoryLedger).where(
            InventoryLedger.user_id == self.user_id,
            InventoryLedger.product_id == product_id,
        )
        return self.session.scalars(stmt).all()
