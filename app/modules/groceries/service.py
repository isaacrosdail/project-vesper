"""
Service layer for Groceries module.
Business logic, multiple repo calls, business rule validation (beyond basic data validation), & cross-module ops (eg, user service calling habit repo)
"""
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.validators import parse_and_validate_form_data


class GroceriesService:
    
    def __init__(self, repository: GroceriesRepository):
        self.repo = repository

    def process_transaction_form(self, form_data: dict):
        """Process transaction form submission."""
        # Validate/parse
        product_data, transaction_data, error = parse_and_validate_form_data(form_data)

        if error:
            return {
                "success": False,
                "message": "Error",
                "show_product_fields": False,
                "form_data": form_data
            }

        # Check if product exists
        product = self.repo.get_product_by_barcode(product_data["barcode"])

        # A: Product exists => Add/increment transaction
        if product:
            self.repo.add_or_increment_transaction(product, **transaction_data)
            return {
                "success": True,
                "message": "Transaction added!",
            }

        # B: Product doesn't exist but we have net_weight filled => create product+transaction
        elif product_data["net_weight"] != "":
            new_product = self.repo.get_or_create_product(**product_data)
            self.repo.add_or_increment_transaction(new_product, **transaction_data)
            return {
                "success": True,
                "message": "Product & transaction added!"
            }

        # C: Product doesn't exist & we don't have info => Show product fields for resubmit
        else:
            return {
                "success": False,
                "message": "Associated product not found. Please add product info.",
                "show_product_fields": True,
                "form_data": form_data
            }