"""
Service layer for Groceries module.
"""
from app.modules.api.responses import service_response
from app.modules.groceries.repository import GroceriesRepository
from app.shared.datetime.helpers import today_range_utc


class GroceriesService:
    
    def __init__(self, repository: GroceriesRepository):
        self.repo = repository

    def create_product(self, typed_data: dict):
        # NOTE: Simple for now, but plan to expand. Therefore keeping this in service.
        product, was_created = self.get_or_create_product(typed_data)
        message = "Product created successfully" if was_created else "Product already exists"
        return service_response(True, message, data={"product": product})


    def create_transaction(self, typed_barcode,typed_transaction_data, typed_product_data=None):
        """Process transaction form submission."""
        product = self.repo.get_product_by_barcode(typed_barcode)

        # Case C: Product doesn't exist & we don't have info => Show product fields for resubmit
        if not product and not typed_product_data:
            return service_response(False, "Product not found", data={"error_type": "product_not_found"})

        # Case B: Product doesn't exist, but we have enough info => create product+transaction
        if not product:
            product = self.repo.create_product(**typed_product_data)

        # Case A: Product exists (fall through, use existing product)
        start_utc, end_utc = today_range_utc(self.repo.user_tz)
        existing = self.repo.get_transaction_in_window(product.id, start_utc, end_utc)

        if existing:
            existing.quantity += typed_transaction_data["quantity"]
        else:
            self.repo.create_transaction(product, **typed_transaction_data)

        return service_response(True, "Transaction added")


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