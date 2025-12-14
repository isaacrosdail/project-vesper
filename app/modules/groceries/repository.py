"""
Repository layer for groceries module.
"""
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import joinedload

from app.modules.groceries.models import (
    Product, Transaction, ShoppingList, ShoppingListItem,
    ProductCategoryEnum, UnitEnum
    )
from app.shared.repository.base import BaseRepository


class GroceriesRepository(BaseRepository[Product]):
    def __init__(self, session: 'Session', user_id: int, user_tz: str):
        super().__init__(session, user_id, user_tz, model_cls=Product)


    def create_product(self, name: str, category: ProductCategoryEnum,
                       net_weight: Decimal, unit_type: UnitEnum,
                       barcode: str | None,
                       calories_per_100g: Decimal | None) -> Product:
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

    def get_all_products(self) -> list[Product]:
        stmt = self._user_select(Product).where(
            Product.deleted_at.is_(None)
        )
        return list(self.session.execute(stmt).scalars().all())
    
    def get_all_products_in_window(self, start_utc: datetime, end_utc: datetime) -> list[Product]:
        stmt = self._user_select(Product).where(
            Product.created_at >= start_utc,
            Product.created_at < end_utc,
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.get_by_id(product_id)

    def get_product_by_barcode(self, barcode: str) -> Product | None:
        stmt = self._user_select(Product).where(
            Product.barcode == barcode,
            Product.deleted_at.is_(None)
        )
        result = self.session.execute(stmt).scalars().first()
        return cast(Product | None, result)

    def get_product_by_name(self, name: str) -> Product | None:
        stmt = self._user_select(Product).where(
            Product.name == name,
            Product.deleted_at.is_(None)
        )
        result = self.session.execute(stmt).scalars().first()
        return cast(Product | None, result)


    def create_transaction(self, product: Product, price_at_scan: Decimal,
                           quantity: int) -> Transaction:
        transaction = Transaction(
            user_id=self.user_id,
            product_id=product.id,
            price_at_scan=price_at_scan,
            quantity=quantity,
        )
        return self.add(transaction)

    def get_all_transactions(self) -> list[Transaction]:
        """Get all transaction for current user with eager-loaded products."""
        stmt = self._user_select(Transaction).options(
            joinedload(Transaction.product)
        )
        return list(self.session.execute(stmt).scalars().all())
    
    def get_all_transactions_in_window(self, start_utc: datetime, end_utc: datetime) -> list[Transaction]:
        """"""
        stmt = self._user_select(Transaction).where(
            Transaction.created_at >= start_utc,
            Transaction.created_at < end_utc,
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_transaction_by_id(self, transaction_id: int) -> Transaction | None:
        stmt = self._user_select(Transaction).where(
            Transaction.id == transaction_id
        )
        result = self.session.execute(stmt).scalars().first()
        return cast(Transaction | None, result)

    def get_transaction_in_window(self, product_id: int, start_utc: datetime, end_utc: datetime) -> Transaction | None:
        """Get a transaction within a certain datetime window (UTC)."""
        stmt = self._user_select(Transaction).where(
            Transaction.product_id == product_id,
            Transaction.created_at >= start_utc,
            Transaction.created_at < end_utc,
        )
        result = self.session.execute(stmt).scalars().first()
        return cast(Transaction | None, result)

    def create_shoppinglist(self, name: str = "DefaultListName") -> ShoppingList:
        shopping_list = ShoppingList(
            user_id=self.user_id,
            name=name
        )
        return self.add(shopping_list)

    # One list per user, for now
    def get_shopping_list(self) -> ShoppingList | None:
        stmt = self._user_select(ShoppingList)
        result = self.session.execute(stmt).scalars().first()
        return cast(ShoppingList | None, result)

    def create_shopping_list_item(self, shopping_list_id: int, product_id: int, quantity_wanted: int) -> ShoppingListItem:
        shopping_list_item = ShoppingListItem(
            user_id=self.user_id,
            shopping_list_id=shopping_list_id,
            product_id=product_id,
            quantity_wanted=quantity_wanted
        )
        return self.add(shopping_list_item)

    def get_shopping_list_item(self, shopping_list_id: int, product_id: int) -> ShoppingListItem | None:
        stmt = self._user_select(ShoppingListItem).where(
            ShoppingListItem.shopping_list_id == shopping_list_id,
            ShoppingListItem.product_id == product_id
        )
        result = self.session.execute(stmt).scalars().first()
        return cast(ShoppingListItem | None, result)
