
# Product field constraints

# Name
PRODUCT_NAME_MAX_LENGTH = 80
PRODUCT_BARCODE_MAX_LENGTH = 32

PRODUCT_NAME_REQUIRED = "Product name is required"
PRODUCT_NAME_TOO_LONG = f"Product name cannot exceed {PRODUCT_NAME_MAX_LENGTH} characters"

# Barcode
BARCODE_MIN_LENGTH = 8
BARCODE_MAX_LENGTH = 32
BARCODE_REGEX = rf'^[A-Za-z0-9]{{{BARCODE_MIN_LENGTH},{BARCODE_MAX_LENGTH}}}$'  # Alphanumeric for UPC/QR/UUID support

BARCODE_REQUIRED = "Barcode is required"
BARCODE_INVALID = f"Barcode must be alphanumeric and consist of {BARCODE_MIN_LENGTH}-{BARCODE_MAX_LENGTH} characters"


# Transaction field constraints  
TRANSACTION_PRICE_MAX_DIGITS = 7  # Total digits (99999.99)
TRANSACTION_PRICE_DECIMAL_PLACES = 2

# Shopping list constraints
SHOPPING_LIST_NAME_MAX_LENGTH = 64

SHOPPING_LIST_NAME_TOO_LONG = f"Shopping list name must be {SHOPPING_LIST_NAME_MAX_LENGTH} or fewer characters"

# Net weight constraints (Numeric(7, 3))
NET_WEIGHT_PRECISION = 7
NET_WEIGHT_SCALE = 3
NET_WEIGHT_MINIMUM = 0

NET_WEIGHT_REQUIRED = "Net weight is required"
NET_WEIGHT_POSITIVE = "Net weight must be greater than 0"
NET_WEIGHT_INVALID = "Net weight must be a valid number"

# Calories constraint (Numeric(5, 2))
CALORIES_PRECISION = 5
CALORIES_SCALE = 2
CALORIES_MINIMUM = 0

CALORIES_NEGATIVE = "Calories cannot be negative"
CALORIES_INVALID = "Calories must be a valid number"

# Validation patterns


CATEGORY_INVALID = "Invalid category"
CATEGORY_REQUIRED = "Category is required"
CATEGORY_LENGTH = "Category must be 100 or fewer characters"

UNIT_TYPE_REQUIRED = "Unit type is required"
UNIT_TYPE_INVALID = "Invalid unit type"

# price_at_scan constraints
PRICE_PRECISION = 7
PRICE_SCALE = 2

PRICE_REQUIRED = "Price is required"
PRICE_NEGATIVE = "Price cannot be negative"
PRICE_INVALID = "Price must be a valid number"

QUANTITY_REQUIRED = "Quantity is required"
QUANTITY_POSITIVE = "Quantity must be greater than 0"
QUANTITY_INVALID = "Quantity must be a valid whole number"

QUANTITY_WANTED_REQUIRED = "Quantity is required"
QUANTITY_WANTED_POSITIVE = "Quantity must be greater than 0" 
QUANTITY_WANTED_INVALID = "Quantity must be a valid whole number"
PRODUCT_REQUIRED = "Product is required"


SHOPPING_LIST_ID_REQUIRED = "Shopping List ID is required"
SHOPPING_LIST_ID_INVALID = "Invalid shopping list ID"

PRODUCT_ID_INVALID = "Product ID is invalid"
PRODUCT_ID_REQUIRED = "Product ID is required"