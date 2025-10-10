from typing import Any

import regex

from app.modules.groceries.constants import *
from app.modules.groceries.models import ProductCategoryEnum, UnitEnum
from app.shared.validators import *


def validate_product_name(product_name: str) -> tuple[str | None, list[str]]:
    """Required. String, max 50 chars."""
    if not product_name:
        return (None, [PRODUCT_NAME_REQUIRED])
    if len(product_name) > PRODUCT_NAME_MAX_LENGTH:
        return (None, [PRODUCT_NAME_TOO_LONG])

    return (product_name, [])


def validate_category(category: str) -> tuple[Any, list[str]]:
    """Required. Valid ProductCategoryEnum value."""
    return validate_enum(category, ProductCategoryEnum, CATEGORY_REQUIRED, CATEGORY_INVALID)


def validate_barcode(barcode: str) -> tuple[str | None, list[str]]:
    """Optional. Alphanumeric string."""
    if not barcode:
        return (None, [])
    if not regex.match(BARCODE_REGEX, barcode):
        return (None, [BARCODE_INVALID])
    
    return (barcode, [])


def validate_net_weight(net_weight: str) -> tuple[float | None, list[str]]:
    """Required. Numeric(7,3), positive."""
    if not net_weight:
        return (None, [NET_WEIGHT_REQUIRED])

    is_valid, error_type = validate_numeric(net_weight,
                        NET_WEIGHT_PRECISION,
                        NET_WEIGHT_SCALE, 
                        NET_WEIGHT_MINIMUM)
    if not is_valid:
        if error_type in [FORMAT_ERROR, PRECISION_EXCEEDED, SCALE_EXCEEDED]:
            return (None, [NET_WEIGHT_INVALID])
        elif error_type == CONSTRAINT_VIOLATION:
            return (None, [NET_WEIGHT_POSITIVE])

    net_weight_float = float(net_weight)
    return (net_weight_float, [])


def validate_unit_type(unit_type: str) -> tuple[Any, list[str]]:
    """Required. Valid UnitEnum value."""
    return validate_enum(unit_type, UnitEnum, UNIT_TYPE_REQUIRED, UNIT_TYPE_INVALID)


def validate_calories(calories: str) -> tuple[float | None, list[str]]:
    """Optional. Numeric(5,2), non-negative."""
    if calories:
        is_valid, error_type = validate_numeric(calories,
                                             CALORIES_PRECISION,
                                             CALORIES_SCALE,
                                             CALORIES_MINIMUM)
        if not is_valid:
            if error_type in [FORMAT_ERROR, PRECISION_EXCEEDED, SCALE_EXCEEDED]:
                return (None, [CALORIES_INVALID])
            elif error_type == CONSTRAINT_VIOLATION:
                return (None, [CALORIES_NEGATIVE])

        calories_float = float(calories)
        return (calories_float, [])
    
    return (None, [])


PRODUCT_VALIDATION_FUNCS = {
    "name": validate_product_name,
    "category": validate_category,
    "barcode": validate_barcode,
    "net_weight": validate_net_weight,
    "unit_type": validate_unit_type,
    "calories_per_100g": validate_calories,
}

def validate_product(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate product data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in PRODUCT_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    return (typed_data, errors)




def validate_price(price: str) -> tuple[float | None, list[str]]:
    """Required. Numeric(7,2), non-negative."""
    if not price:
        return (None, [PRICE_REQUIRED])

    try:
        price_float = float(price)
        if price_float < 0:
            return (None, [PRICE_NEGATIVE])
    except (ValueError, TypeError):
        return (None, [PRICE_INVALID])

    return (price_float, [])


def validate_quantity(quantity: str) -> tuple[int | None, list[str]]:
    """Required. Positive integer."""
    if not quantity:
        return (None, [QUANTITY_REQUIRED])

    try:
        quantity_int = int(quantity)
        if quantity_int <= 0:
            return (None, [QUANTITY_POSITIVE])
    except (ValueError, TypeError):
        return (None, [QUANTITY_INVALID])

    return (quantity_int, [])


TRANSACTION_VALIDATION_FUNCS = {
    "price_at_scan": validate_price,
    "quantity": validate_quantity,
}

def validate_transaction(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate transaction data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in TRANSACTION_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    return (typed_data, errors)



def validate_shopping_list(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate shopping list data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    name = data.get("name")
    # Name is optional (has default), but if provided, validate length
    if name and len(name) > SHOPPING_LIST_NAME_MAX_LENGTH:
        errors["name"] = [SHOPPING_LIST_NAME_TOO_LONG]
    else:
        typed_data["name"] = name
    return (typed_data, errors)




def validate_quantity_wanted(quantity_wanted: str) -> tuple[int | None, list[str]]:
    """Required. Positive integer."""
    if not quantity_wanted:
        return (None, [QUANTITY_WANTED_REQUIRED])

    try:
        quantity_wanted_int = int(quantity_wanted)
        if quantity_wanted_int <= 0:
            return (None, [QUANTITY_WANTED_POSITIVE])
    except (ValueError, TypeError):
        return (None, [QUANTITY_WANTED_INVALID])

    return (quantity_wanted_int, [])


def validate_shopping_list_id(shopping_list_id: str) -> tuple[int | None, list[str]]:
    """Required. Valid integer ID."""
    return validate_id_field(shopping_list_id, SHOPPING_LIST_ID_REQUIRED, SHOPPING_LIST_ID_INVALID)


def validate_product_id(product_id: str) -> tuple[int | None, list[str]]:
    """Required. Valid integer ID."""
    return validate_id_field(product_id, PRODUCT_ID_REQUIRED, PRODUCT_ID_INVALID)


SHOPPING_LIST_ITEM_VALIDATION_FUNCS = {
    "quantity_wanted": validate_quantity_wanted,
    "shopping_list_id": validate_shopping_list_id,
    "product_id": validate_product_id
}

def validate_shopping_list_item(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate shopping list item. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in SHOPPING_LIST_ITEM_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    return (typed_data, errors)


