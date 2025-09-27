"""
Service layer for Groceries module.
Business logic, multiple repo calls, business rule validation (beyond basic data validation), & cross-module ops (eg, user service calling habit repo)
"""
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.validators import validate_product, validate_transaction


class GroceriesService:
    
    def __init__(self, repository: GroceriesRepository):
        self.repo = repository

    def process_transaction_form(self, form_data: dict):
        """Process transaction form submission."""
        # Parse form data
        product_data = {
            "barcode": form_data.get("barcode", "").strip(),
            "name": form_data.get("name", "").strip(),
            "net_weight": form_data.get("net_weight", "").strip(),
            "category": form_data.get("category", "").strip(),
            "unit_type": form_data.get("unit_type", "").strip(),
            "calories_per_100g": form_data.get("calories_per_100g", "").strip(),
        }

        transaction_data = {
            "price": form_data.get("price_at_scan", "").strip(),
            "quantity": form_data.get("quantity", "").strip()
        }

        product_errors = validate_product(product_data)
        transaction_errors = validate_transaction(transaction_data)

        all_errors = {**product_errors, **transaction_errors}
        if all_errors:
            return {"success": False, "errors": all_errors}

        # Check if product exists
        product = self.repo.get_product_by_barcode(product_data["barcode"])

        # A: Product exists => Add/increment transaction
        if product:
            self.repo.add_or_increment_transaction(product, **transaction_data)
            return {"success": True, "message": "Transaction added!"}

        # B: Product doesn't exist but we have net_weight filled => create product+transaction
        elif product_data["net_weight"] != "":
            new_product = self.repo.get_or_create_product(**product_data)
            self.repo.add_or_increment_transaction(new_product, **transaction_data)
            return {"success": True, "message": "Product & transaction added!"}

        # C: Product doesn't exist & we don't have info => Show product fields for resubmit
        else:
            return {
                "success": False, 
                "message": "Associated product not found. Please add product info.",
                "data": {"error_type": "product_not_found"}
            }