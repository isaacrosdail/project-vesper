"""
Service layer for Groceries module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.groceries.models import Product

from app.api.responses import service_response
from app.modules.groceries.repository import (
    ProductRepository,
    ShoppingListItemRepository,
    ShoppingListRepository,
    TransactionRepository,
)
from app.shared.datetime.helpers import today_range_utc


class GroceriesService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        product_repo: ProductRepository,
        transaction_repo: TransactionRepository,
        shopping_list_repo: ShoppingListRepository,
        shopping_list_item_repo: ShoppingListItemRepository,
    ) -> None:
        self.session = session
        self.product_repo = product_repo
        self.transaction_repo = transaction_repo
        self.shopping_list_repo = shopping_list_repo
        self.shopping_list_item_repo = shopping_list_item_repo
        self.user_tz = user_tz

    def save_product(self, typed_data: dict[str, Any], product_id: int | None) -> Any:
        if product_id:
            product = self.product_repo.get_by_id(product_id)
            if not product:
                return service_response(success=False, message="Product not found")

            # Update fields
            for field, value in typed_data.items():
                setattr(product, field, value)

            return service_response(
                success=True, message="Product updated", data={"product": product}
            )

        else:
            # CREATE
            product = self.product_repo.create_product(
                barcode=typed_data.get("barcode"),
                name=typed_data["name"],
                category=typed_data["category"],
                net_weight=typed_data["net_weight"],
                unit_type=typed_data["unit_type"],
                calories_per_100g=typed_data.get("calories_per_100g"),
            )
            self.session.flush()  # TODO: Needed? original note: might need ID for transaction downstream

            return service_response(
                success=True, message="Product created", data={"product": product}
            )

    def save_transaction(
        self,
        product_id: int,
        typed_data: dict[str, Any],
        transaction_id: int | None = None,
    ) -> Any:
        """Process transaction form submission."""

        ### UPDATE
        if transaction_id:
            transaction = self.transaction_repo.get_by_id(transaction_id)
            if not transaction:
                return service_response(success=False, message="Transaction not found")

            for field, value in typed_data.items():
                setattr(transaction, field, value)

            return service_response(
                success=True,
                message="Transaction updated",
                data={"transaction": transaction},
            )

        # CREATE / INCREMENT
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return service_response(success=False, message="Product not found")
        start_utc, end_utc = today_range_utc(self.user_tz)
        existing_transaction = self.transaction_repo.get_transaction_in_window(
            product.id, start_utc, end_utc
        )

        if existing_transaction and (
            existing_transaction.price_at_scan == typed_data["price_at_scan"]
        ):
            existing_transaction.quantity += typed_data["quantity"]
            transaction = existing_transaction
        else:
            transaction = self.transaction_repo.create_transaction(
                product, **typed_data
            )
            self.session.flush()

        return service_response(
            success=True, message="Transaction added", data={"transaction": transaction}
        )

    def add_item_to_shoppinglist(
        self, product_id: int, quantity_wanted: int
    ) -> dict[str, Any]:
        """Add product to shopping list, incrementing if already exists."""
        shopping_list, _ = self.get_or_create_shoppinglist()

        existing_item = self.shopping_list_item_repo.get_shopping_list_item(
            shopping_list.id, product_id
        )

        if existing_item:
            existing_item.quantity_wanted += 1  # NOTE: Take qty as parameter
            self.shopping_list_item_repo.session.flush()
            return service_response(
                success=True,
                message="Quantity updated in shopping list",
                data={"item": existing_item},
            )
        else:
            item = self.shopping_list_item_repo.create_shopping_list_item(
                shopping_list.id, product_id, quantity_wanted
            )
            self.shopping_list_item_repo.session.flush()
            return service_response(
                success=True, message="Item added to shopping list", data={"item": item}
            )

    def get_or_create_shoppinglist(self) -> tuple[Any, Any]:
        """Return ShoppingList from database, else create new and return that."""
        shopping_list = self.shopping_list_repo.get_shopping_list()

        if shopping_list:
            return shopping_list, False
        return self.shopping_list_repo.create_shoppinglist(), True

    def get_or_create_product(
        self, typed_product_data: dict[str, Any]
    ) -> tuple[Product, bool]:
        """Get existing product or create new one. Returns tuple (product, was_created)."""
        barcode = typed_product_data["barcode"]
        product = self.product_repo.get_product_by_barcode(barcode)
        if product:
            return product, False
        return self.product_repo.create_product(**typed_product_data), True


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
    )
