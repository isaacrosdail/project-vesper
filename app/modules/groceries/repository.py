"""
Repository layer for groceries module.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import joinedload

from app.modules.groceries.models import Product, Transaction, UnitEnum, ShoppingList, ShoppingListItem, ProductCategoryEnum
from app.shared.repository.base import BaseRepository


class GroceriesRepository(BaseRepository):
    def __init__(self, session, user_id, user_tz):
        super().__init__(session, user_id, user_tz, model_cls=Product)


    def get_product_by_barcode(self, barcode: str):
        return self._user_query(Product).filter(
            Product.barcode == barcode,
            Product.deleted_at.is_(None)
        ).first()
    
    def get_product_by_name(self, name: str):
        return self._user_query(Product).filter(
            Product.name == name,
            Product.deleted_at.is_(None)
        )

    def get_product_by_id(self, product_id: int):
        return self.get_by_id(product_id)

    def get_all_products(self):
        return self._user_query(Product).filter(
            Product.deleted_at.is_(None)
        ).all()


    # TODO: NOTES: Eager load 'product' relationship using joinedload so we can safely access transaction.product.* fields in templates
    # after session is closed (avoids DetachedInstanceError)
    def get_all_transactions(self):
        """Get all transaction for current user with eager-loaded products."""
        return self._user_query(Transaction).options(
            joinedload(Transaction.product)
        ).all()

    def get_transaction_in_window(self, product_id: int, start_utc: datetime, end_utc: datetime):
        """Get a transaction within a certain datetime window (UTC)."""
        return self._user_query(Transaction).filter(
            Transaction.product_id == product_id,
            Transaction.created_at >= start_utc,
            Transaction.created_at < end_utc,
        ).first()


    def create_product(self, barcode: str, name: str, category: ProductCategoryEnum,
                       net_weight: Decimal, unit_type: UnitEnum,
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

        
    def create_transaction(self, product: Product, price_at_scan: Decimal,
                           quantity: int) -> Transaction:
        transaction = Transaction(
            user_id=self.user_id,
            product_id=product.id,
            price_at_scan=price_at_scan,
            quantity=quantity,
        )
        return self.add(transaction)

        
    def create_shoppinglist(self, name: str = "DefaultListName"):
        shopping_list = ShoppingList(
            user_id=self.user_id,
            name=name
        )
        return self.add(shopping_list)

    # One list per user, for now
    def get_shopping_list(self):
        return self._user_query(ShoppingList).first()
    
    def get_shopping_list_item(self, shopping_list_id: int, product_id: int) -> ShoppingListItem:
        return self._user_query(ShoppingListItem).filter(
            ShoppingListItem.shopping_list_id == shopping_list_id,
            ShoppingListItem.product_id == product_id
        ).first()

    def create_shopping_list_item(self, shopping_list_id: int, product_id: int) -> ShoppingListItem:
        shopping_list_item = ShoppingListItem(
            user_id=self.user_id,
            shopping_list_id=shopping_list_id,
            product_id=product_id
        )
        return self.add(shopping_list_item)