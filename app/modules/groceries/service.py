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
        product = self.repo.create_product(
            barcode=typed_data.get("barcode"),
            name=typed_data["name"],
            category=typed_data["category"],
            net_weight=typed_data["net_weight"],
            unit_type=typed_data["unit_type"],
            calories_per_100g=typed_data.get("calories_per_100g"),
        )
        self.repo.session.flush() # might need ID for transaction downstream

        return service_response(True, "Product created", data={"product": product})


    def create_transaction(self, product_id: int, typed_transaction_data: dict):
        """Process transaction form submission."""
        product = self.repo.get_product_by_id(product_id)

        start_utc, end_utc = today_range_utc(self.repo.user_tz)
        existing = self.repo.get_transaction_in_window(product.id, start_utc, end_utc)

        if existing and (existing.price_at_scan == typed_transaction_data["price_at_scan"]):
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