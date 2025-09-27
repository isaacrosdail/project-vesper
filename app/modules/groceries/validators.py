import regex

from app.modules.groceries.models import UnitEnum, ProductCategoryEnum
from app.modules.groceries.constants import *
from app.shared.validators import *


def validate_shopping_list(data: dict) -> dict[str, list[str]]:
    errors = {}

    name = data["name"]
    # Name is optional (has default), but if provided, validate length
    if name and len(name) > SHOPPING_LIST_NAME_MAX_LENGTH:
        errors["name"] = [SHOPPING_LIST_NAME_TOO_LONG]

    return errors

def validate_quantity_wanted(quantity:str) -> list[str]:
    errors = []
    if not quantity:
        errors.append(QUANTITY_WANTED_REQUIRED)
    else:
        try:
            qty_val = int(quantity)
            if qty_val <= 0:
                errors.append(QUANTITY_WANTED_POSITIVE)
        except (ValueError, TypeError):
            errors.append(QUANTITY_WANTED_INVALID)
    return errors

def validate_product_id(product_id: str) -> list[str]:
    return validate_id_field(product_id, PRODUCT_ID_REQUIRED, PRODUCT_ID_INVALID)

def validate_shopping_list_id(shopping_list_id: str) -> list[str]:
    return validate_id_field(shopping_list_id, SHOPPING_LIST_ID_REQUIRED, SHOPPING_LIST_ID_INVALID)


SHOPPING_LIST_ITEM_VALIDATION_FUNCS = {
    "quantity_wanted": validate_quantity_wanted,
    "product_id": validate_product_id,
    "shopping_list_id": validate_shopping_list_id
}

def validate_shopping_list_item(data: dict) -> dict[str, list[str]]:
    errors = {}

    for field, func in SHOPPING_LIST_ITEM_VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
    return errors



def validate_product_name(product_name: str) -> list[str]:
    errors = []
    if not product_name:
        errors.append(PRODUCT_NAME_REQUIRED)
    elif len(product_name) > PRODUCT_NAME_MAX_LENGTH:
        errors.append(PRODUCT_NAME_TOO_LONG)
    return errors

def validate_barcode(barcode: str) -> list[str]:
    errors = []
    if not barcode:
        errors.append(BARCODE_REQUIRED)
    elif not regex.match(BARCODE_REGEX, barcode):
        errors.append(BARCODE_INVALID)
    return errors

def validate_net_weight(net_weight: str) -> list[str]:
    errors = []
    if not net_weight:
        errors.append(NET_WEIGHT_REQUIRED)
    else:
        is_valid, error_type = validate_numeric(net_weight,
                           NET_WEIGHT_PRECISION,
                           NET_WEIGHT_SCALE, 
                           NET_WEIGHT_MINIMUM)
        if not is_valid:
            if error_type in [FORMAT_ERROR, PRECISION_EXCEEDED, SCALE_EXCEEDED]:
                errors.append(NET_WEIGHT_INVALID)
            elif error_type == CONSTRAINT_VIOLATION:
                errors.append(NET_WEIGHT_POSITIVE)
    return errors

def validate_unit_type(unit_type: str) -> list[str]:
    return validate_enum(unit_type, UnitEnum, UNIT_TYPE_REQUIRED, UNIT_TYPE_INVALID)

def validate_category(category: str) -> list[str]:
    return validate_enum(category, ProductCategoryEnum, CATEGORY_REQUIRED, CATEGORY_INVALID)


def validate_calories(calories: str) -> list[str]:
    """Non-negative Numeric(5,2)"""
    errors = []
    if calories:
        is_valid, error_type = validate_numeric(calories,
                                             CALORIES_PRECISION,
                                             CALORIES_SCALE,
                                             CALORIES_MINIMUM)
        if not is_valid:
            if error_type in [FORMAT_ERROR, PRECISION_EXCEEDED, SCALE_EXCEEDED]:
                errors.append(CALORIES_INVALID)
            elif error_type == CONSTRAINT_VIOLATION:
                errors.append(CALORIES_NEGATIVE)
    return errors

def validate_price(price: str) -> list[str]:
    errors = []
    if not price:
        errors.append(PRICE_REQUIRED)
    else:
        try:
            price_value = float(price)
            if price_value < 0:
                errors.append(PRICE_NEGATIVE)
        except (ValueError, TypeError):
            errors.append(PRICE_INVALID)

    return errors

def validate_quantity(quantity: str) -> list[str]:
    errors = []
    if not quantity:
        errors.append(QUANTITY_REQUIRED)
    else:
        try:
            qty_value = int(quantity)
            if qty_value <= 0:
                errors.append(QUANTITY_POSITIVE)
        except (ValueError, TypeError):
            errors.append(QUANTITY_INVALID)

    return errors


PRODUCT_VALIDATION_FUNCS = {
    "name": validate_product_name,
    "barcode": validate_barcode,
    "net_weight": validate_net_weight,
    "unit_type": validate_unit_type,
    "category": validate_category,
    "calories_per_100g": validate_calories,
}

def validate_product(data: dict) -> dict[str, list[str]]:
    errors = {}

    for field, func in PRODUCT_VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors

    return errors



TRANSACTION_VALIDATION_FUNCS = {
    "price_at_scan": validate_price,
    "quantity": validate_quantity,
}

def validate_transaction(data: dict) -> dict[str, list[str]]:
    errors = {}

    for field, func in TRANSACTION_VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors

    return errors