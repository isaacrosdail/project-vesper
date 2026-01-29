
from app.shared.validation_messages import (
    invalid,
    invalid_range,
    negative,
    positive,
    required,
    too_long,
)

# Name
PRODUCT_NAME_MAX_LENGTH = 80
PRODUCT_NAME_REQUIRED = required("Product name")
PRODUCT_NAME_TOO_LONG = too_long("Product name", PRODUCT_NAME_MAX_LENGTH)

# Barcode
BARCODE_MIN_LENGTH = 8
BARCODE_MAX_LENGTH = 32
# Alphanumeric for UPC/QR/UUID support
BARCODE_REGEX = rf"^[A-Za-z0-9]{{{BARCODE_MIN_LENGTH},{BARCODE_MAX_LENGTH}}}$"

BARCODE_REQUIRED = required("Barcode")
BARCODE_INVALID = invalid_range("Barcode", BARCODE_MIN_LENGTH, BARCODE_MAX_LENGTH)

# Transaction
TRANSACTION_PRICE_MAX_DIGITS = 7  # total digits (99999.99)
TRANSACTION_PRICE_DECIMAL_PLACES = 2

# Shopping list
SHOPPING_LIST_NAME_MAX_LENGTH = 64
SHOPPING_LIST_NAME_TOO_LONG = too_long("Shopping list", SHOPPING_LIST_NAME_MAX_LENGTH)

# Net weight (Numeric(7, 3))
NET_WEIGHT_PRECISION = 7
NET_WEIGHT_SCALE = 3
NET_WEIGHT_MINIMUM = 0

NET_WEIGHT_REQUIRED = required("Net weight")
NET_WEIGHT_POSITIVE = positive("Net weight")
NET_WEIGHT_INVALID = invalid("Net weight")

# Calories (float)
CALORIES_MINIMUM = 0
CALORIES_NEGATIVE = negative("Calories")
CALORIES_INVALID = invalid("Calories")

# Category (Enums)
CATEGORY_REQUIRED = required("Category")
CATEGORY_INVALID = invalid("Category")

# Unit Type (Enums)
UNIT_TYPE_REQUIRED = required("unit_type")
UNIT_TYPE_INVALID = invalid("unit_type")

# Price at scan
PRICE_PRECISION = 7
PRICE_SCALE = 2
PRICE_REQUIRED = required("Price")
PRICE_NEGATIVE = negative("Price")
PRICE_INVALID = invalid("Price")

# Quantity
QUANTITY_REQUIRED = required("Quantity")
QUANTITY_POSITIVE = positive("Quantity")
QUANTITY_INVALID = invalid("quantity")

# Quantity Wanted
QUANTITY_WANTED_REQUIRED = required("quantity_wanted")
QUANTITY_WANTED_POSITIVE = positive("quantity_wanted")
QUANTITY_WANTED_INVALID = invalid("quantity_wanted")

# Relationships
PRODUCT_REQUIRED = required("Product")
PRODUCT_ID_REQUIRED = required("Product ID")
PRODUCT_ID_INVALID = invalid("Product ID")

SHOPPING_LIST_ID_REQUIRED = required("Shopping list ID")
SHOPPING_LIST_ID_INVALID = invalid("Shopping list ID")
