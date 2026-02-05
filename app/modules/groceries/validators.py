from typing import Any

import regex

from app.modules.groceries import validation_constants as c
from app.modules.groceries.models import ProductCategoryEnum, UnitEnum
from app.shared.decorators import log_validator
from app.shared.type_defs import ValidatorFunc
from app.shared.validators import (
    CONSTRAINT_VIOLATION,
    FORMAT_ERROR,
    PRECISION_EXCEEDED,
    SCALE_EXCEEDED,
    validate_numeric,
    validate_optional_int,
    validate_required_enum,
    validate_required_int,
    validate_required_string,
)

def validate_barcode(barcode: str | None) -> tuple[str | None, list[str]]:
    """Optional. Alphanumeric string."""
    if not barcode:
        return (None, [])
    if not regex.match(c.BARCODE_REGEX, barcode):
        return (None, [c.BARCODE_INVALID])

    return (barcode, [])


def validate_net_weight(net_weight: str | None) -> tuple[float | None, list[str]]:
    """Required. Numeric(7,3), positive."""
    if not net_weight:
        return (None, [c.NET_WEIGHT_REQUIRED])

    is_valid, error_type = validate_numeric(
        net_weight, c.NET_WEIGHT_PRECISION, c.NET_WEIGHT_SCALE, c.NET_WEIGHT_MINIMUM
    )
    if not is_valid:
        if error_type in {FORMAT_ERROR, PRECISION_EXCEEDED, SCALE_EXCEEDED}:
            return (None, [c.NET_WEIGHT_INVALID])
        elif error_type == CONSTRAINT_VIOLATION:
            return (None, [c.NET_WEIGHT_POSITIVE])

    net_weight_float = float(net_weight)
    return (net_weight_float, [])


PRODUCT_VALIDATION_FUNCS: dict[str, ValidatorFunc] = {
    "name": lambda v: validate_required_string(
        v, c.PRODUCT_NAME_MAX_LENGTH, c.PRODUCT_NAME_REQUIRED, c.PRODUCT_NAME_TOO_LONG
    ),
    "category": lambda v: validate_required_enum(
        v, ProductCategoryEnum, c.CATEGORY_INVALID, c.CATEGORY_REQUIRED
    ),
    "barcode": validate_barcode,
    "net_weight": validate_net_weight,
    "unit_type": lambda v: validate_required_enum(
        v, UnitEnum, c.UNIT_TYPE_INVALID, c.UNIT_TYPE_REQUIRED
    ),
    "calories_per_100g": lambda v: validate_optional_int(
        v, c.CALORIES_INVALID
    ),
}


@log_validator
def validate_product(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
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


def validate_price(price: str | None) -> tuple[float | None, list[str]]:
    """Required. Numeric(7,2), non-negative."""
    if not price:
        return (None, [c.PRICE_REQUIRED])

    try:
        price_float = float(price)
        if price_float < 0:
            return (None, [c.PRICE_NEGATIVE])
    except (ValueError, TypeError):
        return (None, [c.PRICE_INVALID])

    return (price_float, [])


TRANSACTION_VALIDATION_FUNCS: dict[str, ValidatorFunc] = {
    "price_at_scan": validate_price,
    "quantity": lambda v: validate_required_int(
        v, c.QUANTITY_INVALID, c.QUANTITY_INVALID
    ),
}


@log_validator
def validate_transaction(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
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


@log_validator
def validate_shopping_list(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate shopping list data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    name = data.get("name")
    # Name is optional (has default), but if provided, validate length
    if name and len(name) > c.SHOPPING_LIST_NAME_MAX_LENGTH:
        errors["name"] = [c.SHOPPING_LIST_NAME_TOO_LONG]
    else:
        typed_data["name"] = name
    return (typed_data, errors)


SHOPPING_LIST_ITEM_VALIDATION_FUNCS: dict[str, ValidatorFunc] = {
    "quantity_wanted": lambda val: validate_required_int(
        val, c.QUANTITY_WANTED_INVALID, c.QUANTITY_WANTED_REQUIRED
    ),
    "shopping_list_id": lambda val: validate_required_int(
        val, c.SHOPPING_LIST_ID_INVALID, c.SHOPPING_LIST_ID_REQUIRED
    ),
    "product_id": lambda val: validate_required_int(
        val, c.PRODUCT_ID_INVALID, c.PRODUCT_ID_REQUIRED
    ),
}


@log_validator
def validate_shopping_list_item(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
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
