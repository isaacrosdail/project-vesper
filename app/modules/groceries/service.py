"""
Service layer for Groceries module.
"""
from app.api.responses import service_response
from app.modules.groceries.repository import GroceriesRepository
from app.shared.datetime.helpers import today_range_utc


class GroceriesService:
    
    def __init__(self, repository: GroceriesRepository):
        self.repo = repository

    def save_product(self, typed_data: dict, product_id: int | None):

        if product_id:
            product = self.repo.get_product_by_id(product_id)
            if not product:
                return service_response(False, "Product not found")
            
            # Update fields
            for field, value in typed_data.items():
                setattr(product, field, value)

            return service_response(True, "Product updated", data={"product": product})

        else:
            # CREATE
            product = self.repo.create_product(
                barcode=typed_data.get("barcode"),
                name=typed_data["name"],
                category=typed_data["category"],
                net_weight=typed_data["net_weight"],
                unit_type=typed_data["unit_type"],
                calories_per_100g=typed_data.get("calories_per_100g"),
            )
            self.repo.session.flush() # TODO: Needed? original note: might need ID for transaction downstream

            return service_response(True, "Product created", data={"product": product})


    def save_transaction(self, product_id: int, typed_data: dict, transaction_id: int | None = None):
        """Process transaction form submission."""

        ### UPDATE
        if transaction_id:
            transaction = self.repo.get_transaction_by_id(transaction_id)
            if not transaction:
                return service_response(False, "Transaction not found")
            
            for field, value in typed_data.items():
                setattr(transaction, field, value)

            return service_response(True, "Transaction updated", data={"transaction": transaction})
        
        # CREATE / INCREMENT
        product = self.repo.get_product_by_id(product_id)
        start_utc, end_utc = today_range_utc(self.repo.user_tz)
        existing_transaction = self.repo.get_transaction_in_window(product.id, start_utc, end_utc)

        if existing_transaction and (existing_transaction.price_at_scan == typed_data["price_at_scan"]):
            existing_transaction.quantity += typed_data["quantity"]
            transaction = existing_transaction
        else:
            transaction = self.repo.create_transaction(product, **typed_data)

        return service_response(True, "Transaction added", data={"transaction": transaction})


    def add_item_to_shoppinglist(self, product_id):
        """Add product to shopping list, incrementing if already exists."""
        shopping_list, _ = self.get_or_create_shoppinglist()

        existing_item = self.repo.get_shopping_list_item(shopping_list.id, product_id)

        if existing_item:
            existing_item.quantity_wanted += 1 # TODO: Take qty as parameter
            self.repo.session.flush()
            return existing_item, False
        else:
            item = self.repo.create_shopping_list_item(shopping_list.id, product_id)
            self.repo.session.flush()
            return item, True
        
    def get_or_create_shoppinglist(self):
        """Return ShoppingList from database, else create new and return that."""
        shopping_list = self.repo.get_shopping_list()

        if shopping_list:
            return shopping_list, False
        return self.repo.create_shoppinglist(), True

    def get_or_create_product(self, typed_product_data):
        """Get existing product or create new one. Returns tuple (product, was_created)."""
        barcode = typed_product_data["barcode"]
        product = self.repo.get_product_by_barcode(barcode)
        if product:
            return product, False
        return self.repo.create_product(**typed_product_data), True