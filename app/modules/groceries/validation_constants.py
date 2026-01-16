# Product field

# Name
PRODUCT_NAME_MAX_LENGTH = 80
PRODUCT_NAME_REQUIRED = "Product name is required"
PRODUCT_NAME_TOO_LONG = (
    f"Product name cannot exceed {PRODUCT_NAME_MAX_LENGTH} characters"
)

# Barcode
BARCODE_MIN_LENGTH = 8
BARCODE_MAX_LENGTH = 32
# Alphanumeric for UPC/QR/UUID support
BARCODE_REGEX = rf"^[A-Za-z0-9]{{{BARCODE_MIN_LENGTH},{BARCODE_MAX_LENGTH}}}$"

BARCODE_REQUIRED = "Barcode is required"
BARCODE_INVALID = (
    f"Barcode must be {BARCODE_MIN_LENGTH}-{BARCODE_MAX_LENGTH} alphanumeric characters"
)

# Transaction
TRANSACTION_PRICE_MAX_DIGITS = 7  # total digits (99999.99)
TRANSACTION_PRICE_DECIMAL_PLACES = 2

# Shopping list
SHOPPING_LIST_NAME_MAX_LENGTH = 64
SHOPPING_LIST_NAME_TOO_LONG = (
    f"Shopping list name must not exceed {SHOPPING_LIST_NAME_MAX_LENGTH} characters"
)

# Net weight (Numeric(7, 3))
NET_WEIGHT_PRECISION = 7
NET_WEIGHT_SCALE = 3
NET_WEIGHT_MINIMUM = 0

NET_WEIGHT_REQUIRED = "Net weight is required"
NET_WEIGHT_POSITIVE = "Net weight must be greater than 0"
NET_WEIGHT_INVALID = "Net weight must be a valid number"

# Calories (Numeric(5, 2))
CALORIES_PRECISION = 5
CALORIES_SCALE = 2
CALORIES_MINIMUM = 0

CALORIES_NEGATIVE = "Calories cannot be negative"
CALORIES_INVALID = "Calories must be a valid number"

# Category (Enums)
CATEGORY_REQUIRED = "Category is required"
CATEGORY_INVALID = "Invalid category"

# Unit Type (Enums)
UNIT_TYPE_REQUIRED = "Unit type is required"
UNIT_TYPE_INVALID = "Invalid unit type"

# Price at scan
PRICE_PRECISION = 7
PRICE_SCALE = 2

PRICE_REQUIRED = "Price is required"
PRICE_NEGATIVE = "Price cannot be negative"
PRICE_INVALID = "Price must be a valid number"

# Quantity
QUANTITY_REQUIRED = "Quantity is required"
QUANTITY_POSITIVE = "Quantity must be greater than 0"
QUANTITY_INVALID = "Quantity must be a valid whole number"

# Quantity Wanted
QUANTITY_WANTED_REQUIRED = "Quantity is required"
QUANTITY_WANTED_POSITIVE = "Quantity must be greater than 0"
QUANTITY_WANTED_INVALID = "Quantity must be a valid whole number"

# Relationships
PRODUCT_REQUIRED = "Product is required"
PRODUCT_ID_REQUIRED = "Product ID is required"
PRODUCT_ID_INVALID = "Product ID is invalid"

SHOPPING_LIST_ID_REQUIRED = "Shopping List ID is required"
SHOPPING_LIST_ID_INVALID = "Invalid shopping list ID"
