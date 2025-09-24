
from app.modules.groceries.models import Unit

PRODUCT_NAME_REQUIRED = "Product name is required"
PRODUCT_NAME_LENGTH = "Product name must be 100 or fewer characters"
BARCODE_REQUIRED = "Barcode is required"
BARCODE_LENGTH = "Barcode must be 16 or fewer characters"
NET_WEIGHT_REQUIRED = "Net weight is required"
NET_WEIGHT_POSITIVE = "Net weight must be greater than 0"
NET_WEIGHT_INVALID = "Net weight must be a valid number"
UNIT_TYPE_REQUIRED = "Unit type is required"
UNIT_TYPE_INVALID = "Invalid unit type"
CATEGORY_LENGTH = "Category must be 100 or fewer characters"
CALORIES_NEGATIVE = "Calories cannot be negative"
CALORIES_INVALID = "Calories must be a valid number"

PRICE_REQUIRED = "Price is required"
PRICE_NEGATIVE = "Price cannot be negative"
PRICE_INVALID = "Price must be a valid number"
QUANTITY_REQUIRED = "Quantity is required"
QUANTITY_POSITIVE = "Quantity must be greater than 0"
QUANTITY_INVALID = "Quantity must be a valid whole number"
PRODUCT_ID_INVALID = "Invalid product ID"

SHOPPING_LIST_NAME_LENGTH = "Shopping list name must be 100 or fewer characters"

QUANTITY_WANTED_REQUIRED = "Quantity is required"
QUANTITY_WANTED_POSITIVE = "Quantity must be greater than 0" 
QUANTITY_WANTED_INVALID = "Quantity must be a valid whole number"
PRODUCT_REQUIRED = "Product is required"
SHOPPING_LIST_ID_INVALID = "Invalid shopping list ID"


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

	# Name: Required, max 100 chars
	if not name:
		errors.append(PRODUCT_NAME_REQUIRED)
	if name and len(name) > 100:
		errors.append(PRODUCT_NAME_LENGTH)
	
	# Barcode: Required, max 16 chars
	if not barcode:
		errors.append(BARCODE_REQUIRED)
	if barcode and len(barcode) > 16:
		errors.append(BARCODE_LENGTH)
	
	# Validate net_weight (required numeric)
	if not net_weight:
		errors.append(NET_WEIGHT_REQUIRED)
	if net_weight:
		try:
			weight = float(net_weight)
			if weight <= 0:
				errors.append(NET_WEIGHT_POSITIVE)
		except (ValueError, TypeError):
			errors.append(NET_WEIGHT_INVALID)
	
	# Validate unit_type: Required, valid enum
	if not unit_type:
		errors.append(UNIT_TYPE_REQUIRED)
	if unit_type:
		valid_units = [unit.value for unit in Unit]
		if unit_type not in valid_units:
			errors.append(UNIT_TYPE_INVALID)
	
	# TODO: Make category Enum
	# Category (optional): max 100 chars
	if category and len(category) > 100:
		errors.append(CATEGORY_LENGTH)
	
	# Calories (optional): non-negative number
	if calories:
		try:
			calories_val = float(calories)
			if calories_val < 0:
				errors.append(CALORIES_NEGATIVE)
		except:
			errors.append(CALORIES_INVALID)

	return errors

def validate_transaction(data: dict) -> list[str]:
	errors = []

	# Clean/normalize data
	price = data.get("price_at_scan", "")
	quantity = data.get("quantity", "")
	product_id = data.get("product_id")

	# Price
	if not price:
		errors.append(PRICE_REQUIRED)
	if price:
		try:
			price_value = float(price)
			if price_value < 0:
				errors.append(PRICE_NEGATIVE)
		except (ValueError, TypeError):
			errors.append(PRICE_INVALID)
	
	# Quantity
	if not quantity:
		errors.append(QUANTITY_REQUIRED)
	if quantity:
		try:
			qty_value = int(quantity)
			if qty_value <= 0:
				errors.append(QUANTITY_POSITIVE)
		except (ValueError, TypeError):
			errors.append(QUANTITY_INVALID)
	
	# TODO: Product_id too? Or integrityerror check that in service layer?

	return errors

def validate_shopping_list(data: dict) -> list[str]:
	errors = []
	
	name = data.get("name", "").strip()
    
	# Name is optional (has default), but if provided, validate length
	if name and len(name) > 100:
		errors.append(SHOPPING_LIST_NAME_LENGTH)

	return errors

def validate_shopping_list_item(data: dict) -> list[str]:
	errors = []

	quantity = data.get("quantity_wanted", "")
	product_id = data.get("product_id")
	shopping_list_id = data.get("shopping_list_id")

	# Quantity validation
	if not quantity:
		errors.append(QUANTITY_WANTED_REQUIRED)
	if quantity:
		try:
			qty_val = int(quantity)
			if qty_val <= 0:
				errors.append(QUANTITY_WANTED_POSITIVE)
		except (ValueError, TypeError):
			errors.append(QUANTITY_WANTED_INVALID)

	# Product ID validation
	if product_id is None:
		errors.append(PRODUCT_REQUIRED)
	if product_id is not None:
		try:
			int(product_id)
		except (ValueError, TypeError):
			errors.append(PRODUCT_ID_INVALID)

	# Shopping list ID validation (usually set by system, but just in case)
	if shopping_list_id is not None:
		try:
			int(shopping_list_id)
		except (ValueError, TypeError):
			errors.append(SHOPPING_LIST_ID_INVALID)

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
		errors.append(PRODUCT_REQUIRED)

	return errors