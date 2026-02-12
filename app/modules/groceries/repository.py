"""
Repository layer for groceries module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from decimal import Decimal

    from sqlalchemy.orm import Session


from sqlalchemy.orm import joinedload

from app.modules.groceries.models import (
    Product,
    ProductCategoryEnum,
    ShoppingList,
    ShoppingListItem,
    Transaction,
    Recipe,
    RecipeIngredient,
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
        return list(self.session.execute(stmt).scalars().all())

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
        return list(self.session.execute(stmt).scalars().all())

    def get_product_by_barcode(self, barcode: str) -> Product | None:
        stmt = self._user_select(Product).where(
            Product.barcode == barcode, Product.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalars().first()

    def get_product_by_name(self, name: str) -> Product | None:
        stmt = self._user_select(Product).where(
            Product.name == name, Product.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalars().first()


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Transaction)

    def create_transaction(
        self, product: Product, price_at_scan: Decimal, quantity: int
    ) -> Transaction:
        transaction = Transaction(
            user_id=self.user_id,
            product_id=product.id,
            price_at_scan=price_at_scan,
            quantity=quantity,
        )
        return self.add(transaction)

    def get_all_transactions(self) -> list[Transaction]:
        """Get all transaction for current user with eager-loaded products."""
        stmt = self._user_select(Transaction).options(joinedload(Transaction.product))
        return list(self.session.execute(stmt).scalars().all())

    def get_all_transactions_in_window(
        self, start_utc: datetime, end_utc: datetime
    ) -> list[Transaction]:
        """"""
        stmt = self._user_select(Transaction).where(
            Transaction.created_at >= start_utc,
            Transaction.created_at < end_utc,
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_transaction_in_window(
        self, product_id: int, start_utc: datetime, end_utc: datetime
    ) -> Transaction | None:
        """Get a transaction within a certain datetime window (UTC)."""
        stmt = self._user_select(Transaction).where(
            Transaction.product_id == product_id,
            Transaction.created_at >= start_utc,
            Transaction.created_at < end_utc,
        )
        return self.session.execute(stmt).scalars().first()


class ShoppingListRepository(BaseRepository[ShoppingList]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=ShoppingList)

    def create_shoppinglist(self, name: str = "DefaultListName") -> ShoppingList:
        shopping_list = ShoppingList(user_id=self.user_id, name=name)
        return self.add(shopping_list)

    def get_shopping_list(self) -> ShoppingList | None:
        """Get shopping list for user. One list per user."""
        stmt = self._user_select(ShoppingList)
        return self.session.execute(stmt).scalars().first()


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
        return self.session.execute(stmt).scalars().first()

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

    def get_recipe_with_ingredients(
        self, recipe_id: int
    ) -> Recipe | None:
        stmt = self._user_select(Recipe).where(
            Recipe.id==recipe_id
        ).options(
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.product)
        )
        import sys
        result = self.session.execute(stmt).scalars().unique().one_or_none()
        # print("=== RAW SQLALCHEMY OBJECT ===", file=sys.stderr)
        # print(f"Type: {type(result)}", file=sys.stderr)
        # print(f"result.name: {result.name}", file=sys.stderr)
        # print(f"result.yields: {result.yields}", file=sys.stderr)
        # print(f"result.ingredients type: {type(result.ingredients)}", file=sys.stderr)
        # print(f"result.ingredients length: {len(result.ingredients)}", file=sys.stderr)
        
        # for i, ing in enumerate(result.ingredients):
        #     print(f"\n--- Ingredient {i} ---", file=sys.stderr)
        #     print(f"  Type: {type(ing)}", file=sys.stderr)
        #     print(f"  ing.product_id: {ing.product_id}", file=sys.stderr)
        #     print(f"  ing.amount_value: {ing.amount_value}", file=sys.stderr)
        #     print(f"  ing.amount_units: {ing.amount_units}", file=sys.stderr)
        #     print(f"  hasattr 'product': {hasattr(ing, 'product')}", file=sys.stderr)
        #     if hasattr(ing, 'product'):
        #         print(f"  ing.product: {ing.product}", file=sys.stderr)
        #         print(f"  ing.product.name: {ing.product.name if ing.product else None}", file=sys.stderr)
    
        return result

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