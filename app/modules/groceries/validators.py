# Validation logic for grocery stuff - product/transaction data, etc.
# TODO: Needs attention
from decimal import Decimal


def parse_and_validate_form_data(form_data):
	######## TODO: EXTRACT THIS VALIDATION/ETC STUFF INTO HELPER FUNCTIONS
	# Normalize
	product_data = {
		# Use .get when the field might not be included at all (eg., in our "first pass" for a non-existent product here)
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
	try:
		transaction_data["price"] = Decimal(transaction_data["price"])
	except (ValueError, TypeError):
		return None, None, "Invalid input."

	if not product_data["barcode"]:
		return None, None, "Barcode is required."

	return product_data, transaction_data, None # None = no errors

	# # TODO: Do this
	# def validate_transaction_data(transaction_data, creating_product=False):
	# 	# # If creating_product = True: also validate embedded product fields
	# 	errors = []
	# 	# Transaction fields
	# 	if transaction_data:
	# 		pass
	# 	if creating_product:
	# 		errors += validate_product_data(transaction_data)
	# 	return errors



def validate_product_data(product_data):
	errors = []

	if not product_data.get("name"):
		errors.append("Product name is required.")

	return errors