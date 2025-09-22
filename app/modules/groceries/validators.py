# Validation logic for grocery stuff - product/transaction data, etc.
# TODO: Needs attention
from decimal import Decimal
from app.modules.groceries.models import Unit

def validate_product(data: dict) -> list[str]:
	"""Validate product data. Returns list of error messages."""
	errors = []

	# Clean/normalize data first
	name = data.get("name", "").strip()
	barcode = data.get("barcode", "").strip()
	category = data.get("category", "").strip()
	net_weight = data.get("net_weight", "")
	unit_type = data.get("unit_type", "").strip()
	calories = data.get("calories_per_100g", "")

	# Validate required fields
	if not name:
		errors.append("Product name is required")
	elif len(name) > 100:
		errors.append("Product name must be under 100 characters")
	
	if not barcode:
		errors.append("Barcode is required")
	elif len(barcode) > 64:
		errors.append("Barcode must be under 64 characters")
	
	# Validate net_weight (required numeric)
	if not net_weight:
		errors.append("Net weight is required")
	else:
		try:
			weight = float(net_weight)
			if weight <= 0:
				errors.append("Net weight must be greater than 0")
		except (ValueError, TypeError):
			errors.append("Net weight must be a valid number")
	
	# Validate unit type (required enum)
	if not unit_type:
		errors.append("Unit type is required")
	else:
		valid_units = [unit.value for unit in Unit]
		if unit_type not in valid_units:
			errors.append("Invalid unit type")
	
	# Optional category
	# TODO: Make category Enum
	if category and len(category) > 100:
		errors.append("Category must be under 100 characters")
	
	# Optional calories
	if calories:
		try:
			calories_val = float(calories)
			if calories_val < 0:
				errors.append("Calories cannot be negative")
		except:
			errors.append("Calories must be a valid number!")

	return errors

def validate_transaction(data: dict) -> list[str]:
	errors = []

	# Clean/normalize data
	price = data.get("price_at_scan", "")
	quantity = data.get("quantity", "")
	product_id = data.get("product_id")

	# Price
	if not price:
		errors.append("Price is required")
	else:
		try:
			price_value = float(price)
			if price_value < 0:
				errors.append("Price cannot be negative")
		except (ValueError, TypeError):
			errors.append("Price must be a valid number")
	
	# Quantity
	if not quantity:
		errors.append("Quantity is required")
	else:
		try:
			qty_value = int(quantity)
			if qty_value <= 0:
				errors.append("Quantity must be greater than 0")
		except (ValueError, TypeError):
			errors.append("Quantity must be a valid whole number")
	
	# TODO: Product_id too? Or integrityerror check that in service layer?

	return errors

def validate_shopping_list(data: dict) -> list[str]:
	errors = []
	
	name = data.get("name", "").strip()
    
	# Name is optional (has default), but if provided, validate length
	if name and len(name) > 100:
		errors.append("Shopping list name must be under 100 characters")

	return errors

def validate_shopping_list_item(data: dict) -> list[str]:
	errors = []

	quantity = data.get("quantity_wanted", "")
	product_id = data.get("product_id")
	shopping_list_id = data.get("shopping_list_id")

	# Quantity validation
	if not quantity:
		errors.append("Quantity is required")
	else:
		try:
			qty_val = int(quantity)
	
			if qty_val <= 0:
				errors.append("Quantity must be greater than 0")
		except (ValueError, TypeError):
			errors.append("Quantity must be a valid whole number")

	# Product ID validation
	if product_id is None:
		errors.append("Product is required")
	else:
		try:
			int(product_id)
		except (ValueError, TypeError):
			errors.append("Invalid product ID")

	# Shopping list ID validation (usually set by system, but just in case)
	if shopping_list_id is not None:
		try:
			int(shopping_list_id)
		except (ValueError, TypeError):
			errors.append("Invalid shopping list ID")

	return errors

def parse_and_validate_form_data(form_data):

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

	all_errors = product_errors + transaction_errors
	if all_errors:
		return None, None, all_errors[0]

	return product_data, transaction_data, None # None = no errors


def validate_and_parse_product_data(product_data):
	errors = []

	if not product_data.get("name"):
		errors.append("Product name is required.")

	return errors