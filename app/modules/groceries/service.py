"""
Service layer for Groceries module.
Business logic, multiple repo calls, business rule validation (beyond basic data validation), & cross-module ops (eg, user service calling habit repo)
"""
from decimal import Decimal

from app.modules.groceries.models import UnitEnum
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.validators import validate_product, validate_transaction, validate_barcode
from app.shared.datetime.helpers import today_range_utc
from app.shared.parsers import parse_product_data, parse_transaction_data, parse_barcode
from app.modules.api.responses import service_response


class GroceriesService:
    
    def __init__(self, repository: GroceriesRepository):
        self.repo = repository

    def process_product_form(self, form_data: dict):
        product_data = parse_product_data(form_data)

        typed_product_data, errors = validate_product(product_data)
        if errors:
            return service_response(False, "Validation failed", errors=errors)
        
        product, was_created = self.get_or_create_product(typed_product_data)
        message = "Product created successfully" if was_created else "Product already exists"

        return service_response(True, message, data={"product": product})


    def process_transaction_form(self, form_data: dict, show_product_fields: bool):
        """Process transaction form submission."""

        # 1. Parse + Validate barcode
        barcode = parse_barcode(form_data.get("barcode"))
        typed_barcode, barcode_errors = validate_barcode(barcode)
        if barcode_errors:
            return service_response(
                False,
                "Validation failed",
                errors={"barcode": barcode_errors},
                data={"error_type": "barcode_invalid"}
            )
        
        # 2. Check if product exists
        product = self.repo.get_product_by_barcode(typed_barcode)

        # 3. Always parse/validate transaction (need it either way)
        transaction_data = parse_transaction_data(form_data)
        typed_transaction_data, transaction_errors = validate_transaction(transaction_data)
        if transaction_errors:
            return service_response(
                False,
                "Validation failed",
                errors={"transaction": transaction_errors},
                data={"error_type": "transaction_invalid"}
            )
        
        # 4. Case A: If product exists, we do NOT validate product form fields => Add/increment transaction
        if product:
            self.add_or_increment_transaction(product, **typed_transaction_data)
            return service_response(True, "Transaction added")

        # 5. Case B: Complete submission. Product doesn't exist, but we have enough info => create product+transaction
        elif show_product_fields:
            product_data = parse_product_data(form_data)
            typed_product_data, product_errors = validate_product(product_data)
            if product_errors:
                return service_response(
                    False,
                    "Validation failed",
                    errors={"product": product_errors},
                    data={"error_type": "product_invalid"}
                )
            
            new_product = self.get_or_create_product(**typed_product_data)
            self.add_or_increment_transaction(new_product, **typed_transaction_data)

            return service_response(True, "Product & transaction added")

        # 6. No product exists and not enough info to create one: ask for product details
        # C: Product doesn't exist & we don't have info => Show product fields for resubmit
        else:
            return service_response(
                False,
                "Associated product not found. Please add product info",
                data = {"error_type": "product_not_found"}
            )
        
    def add_or_increment_transaction(self, product, **typed_transaction_data):
        """Add or increment transaction for today. Returns (transaction, was_created)"""
        start_utc, end_utc = today_range_utc()
        existing = self.repo.get_transaction_in_window(product.id, start_utc, end_utc)
        # prepped_data = {
        #     **transaction_data,
        #     "price": Decimal(transaction_data["price_at_scan"]),
        #     "quantity": int(transaction_data["quantity"]),
        # }

        if existing:
            existing.quantity += typed_transaction_data["quantity"]
            return existing, False
        else:
            transaction = self.repo.create_transaction(product, **typed_transaction_data)
            return transaction, True
        

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
        # Cast after validation
        # prepped_data = {
        #     **product_data,
        #     "net_weight": float(product_data["net_weight"]),
        #     "unit_type": UnitEnum(product_data["unit_type"]),
        #     "calories_per_100g": float(product_data["calories_per_100g"])
        #         if product_data["calories_per_100g"] else None,
        # }
        barcode = typed_product_data["barcode"]
        product = self.repo.get_product_by_barcode(barcode)
        if product:
            return product, False
        return self.repo.create_product(**typed_product_data), True