# Validation logic for grocery stuff - product/transaction data, etc.
from app.core.constants import DEFAULT_LANG
from app.core.messages import msg
from decimal import Decimal

def parse_and_validate_form_data(form_data):
    ######## TODO: EXTRACT THIS VALIDATION/ETC STUFF INTO HELPER FUNCTIONS
    # Normalize
    product_data = {
        # Use .get when the field might not be included at all (eg., in our "first pass" for a non-existent product here)
        "barcode": form_data.get("barcode", "").strip(),
        "product_name": form_data.get("product_name", "").strip(),
        "net_weight": form_data.get("net_weight", "").strip(),
        "category": form_data.get("category", "").strip(),
        "unit_type": form_data.get("unit_type", "").strip(),
        "calories_per_100g": form_data.get("calories_per_100g", "").strip(),
    }
    transaction_data = {
        "price": form_data.get("price_at_scan", "").strip(),
        "quantity": form_data.get("quantity", "").strip()
    }
    try:
        transaction_data["price"] = Decimal(transaction_data["price"])
    # TODO: Study/drill this
    except (ValueError, TypeError):
        return None, None, "Invalid input."
	
    if not product_data["barcode"]:
        return None, None, "Barcode is required."
	
    return product_data, transaction_data, None # None = no errors


def validate_product_data(product_data):
	errors = []
    # Minimal, strict input validation
	if not product_data.get("barcode"):
		errors.append(msg("invalid_data", DEFAULT_LANG))
		#raise ValueError("Barcode is required.")
	if not product_data.get("product_name"):
		errors.append(msg("invalid_data", DEFAULT_LANG))
		#raise ValueError("Product name is required.")
	if not product_data.get("category"):
		errors.append(msg("invalid_data", DEFAULT_LANG))
		#raise ValueError("Category is required.")
	if not product_data.get("unit_type"):
		errors.append(msg("invalid_data", DEFAULT_LANG))
		#raise ValueError("Unit type is required.")
	if "net_weight" not in product_data or float(product_data["net_weight"]) <= 0:
		errors.append(msg("invalid_data", DEFAULT_LANG))
		#raise ValueError("Net weight must be positive.")
	return errors

def validate_transaction_data(transaction_data, creating_product=False):
	# # If creating_product = True: also validate embedded product fields
	errors = []
	# if not transaction_data.get("barcode"):
	if transaction_data:
		return errors
	else:
		return errors.append("error")