import pytest

from app.modules.groceries.validators import *
from app.modules.groceries.constants import *
from app.modules.groceries.models import UnitEnum, ProductCategoryEnum


@pytest.mark.parametrize("product_name, expected_value, expected_errors", [
    ("Oranges", "Oranges", []),
    ("", None, [PRODUCT_NAME_REQUIRED]),
    ("a" * 100, None, [PRODUCT_NAME_TOO_LONG]),
])
def test_validate_product_name(product_name, expected_value, expected_errors):
    typed_value, errors = validate_product_name(product_name)
    assert typed_value == expected_value
    assert errors == expected_errors

@pytest.mark.parametrize("category, expected_value, expected_errors", [
    ("DAIRY_EGGS", ProductCategoryEnum.DAIRY_EGGS, []),
    ("", None, [CATEGORY_REQUIRED]),
    ("NOT_A_CATEGORY", None, [CATEGORY_INVALID]),
])
def test_validate_category(category, expected_value, expected_errors):
    typed_value, errors = validate_category(category)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("barcode, expected_value, expected_errors", [
    ("123456789012", "123456789012", []),
    ("", None, [BARCODE_REQUIRED]),
    ("invalid!!", None, [BARCODE_INVALID]),
])
def test_validate_barcode(barcode, expected_value, expected_errors):
    typed_value, errors = validate_barcode(barcode)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("net_weight, expected_value, expected_errors", [
    ("100.00", 100.00, []),
    ("", None, [NET_WEIGHT_REQUIRED]),
    ("abc", None, [NET_WEIGHT_INVALID]),
    ("-5.00", None, [NET_WEIGHT_POSITIVE]),
    ("12.3456", None, [NET_WEIGHT_INVALID]),
    ("9999.999", 9999.999, []), # Max valid value for Numeric(7, 3)
    ("10000.00", None, [NET_WEIGHT_INVALID]), # Exceeds precision (5 digits before decimal)
    ("9999.9999", None, [NET_WEIGHT_INVALID]), # Exceeds scale (4 digits after decimal)
])
def test_validate_net_weight(net_weight, expected_value, expected_errors):
    typed_value, errors = validate_net_weight(net_weight)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("unit_type, expected_value, expected_errors", [
    ("G", UnitEnum.G, []),
    ("", None, [UNIT_TYPE_REQUIRED]),
    ("INVALID", None, [UNIT_TYPE_INVALID]),
    ("", None, [UNIT_TYPE_REQUIRED]),
    (None, None, [UNIT_TYPE_REQUIRED]),
])
def test_validate_unit_type(unit_type, expected_value, expected_errors):
    typed_value, errors = validate_unit_type(unit_type) 
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("calories, expected_value, expected_errors", [
    ("", None, []),
    (None, None, []), # None  should be ignored
    ("200.50", 200.50, []),
    ("-10.00", None, [CALORIES_NEGATIVE]),
    ("not_a_number", None, [CALORIES_INVALID]),
    ("100.123", None, [CALORIES_INVALID]),
])
def test_validate_calories(calories, expected_value, expected_errors):
    typed_value, errors = validate_calories(calories)
    assert typed_value == expected_value
    assert errors == expected_errors



@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"name": "Apples", "barcode": "123456789012", "net_weight": "100.0", "unit_type": "G", "category": "FRUITS"},
        {"name": "Apples", "barcode": "123456789012", "net_weight": 100.0, "unit_type": UnitEnum.G, "category": ProductCategoryEnum.FRUITS},
        {}
    ),
    (
        {"name": "", "barcode": "invalid", "net_weight": "isNaN", "unit_type": "not_valid", "category": "misc"},
        {},
        {
            "name": [PRODUCT_NAME_REQUIRED],
            "barcode": [BARCODE_INVALID],
            "net_weight": [NET_WEIGHT_INVALID],
            "unit_type": [UNIT_TYPE_INVALID],
            "category": [CATEGORY_INVALID]
        }
    )
])
def test_validate_product(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_product(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors





@pytest.mark.parametrize("product_id, expected_value, expected_errors", [
    ("1", 1, []),
    ("", None, [PRODUCT_ID_REQUIRED]),
    ("abc", None, [PRODUCT_ID_INVALID]),
])
def test_validate_product_id(product_id, expected_value, expected_errors):
    typed_value, errors = validate_product_id(product_id)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("price, expected_value, expected_errors", [
    ("1.99", 1.99, []),
    ("", None, [PRICE_REQUIRED]),
    ("-1.00", None, [PRICE_NEGATIVE]),
    ("abc", None, [PRICE_INVALID]),
])
def test_validate_price(price, expected_value, expected_errors):
    typed_value, errors = validate_price(price)
    assert typed_value == expected_value
    assert errors == expected_errors

@pytest.mark.parametrize("transaction_quantity, expected_value, expected_errors", [
    ("5", 5, []),
    ("", None, [QUANTITY_REQUIRED]),
    ("0", None, [QUANTITY_POSITIVE]),
    ("abc", None, [QUANTITY_INVALID]),
])
def test_validate_quantity(transaction_quantity, expected_value, expected_errors):
    typed_value, errors = validate_quantity(transaction_quantity)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"price_at_scan": "5.99", "quantity": "3", "product_id": "4"},
        {"price_at_scan": 5.99, "quantity": 3, "product_id": 4},
        {}
    ),
    (
        {"price_at_scan": "-1.00", "quantity": "0"},
        {},
        {
            "product_id": [PRODUCT_ID_REQUIRED],
            "price_at_scan": [PRICE_NEGATIVE],
            "quantity": [QUANTITY_POSITIVE]
        }
    )
])
def test_validate_transaction(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_transaction(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors




@pytest.mark.parametrize("qty_wanted, expected_value, expected_errors", [
    ("2", 2, []),
    ("", None, [QUANTITY_WANTED_REQUIRED]),
    ("0", None, [QUANTITY_WANTED_POSITIVE]),
    ("abc", None, [QUANTITY_WANTED_INVALID]),
])
def test_validate_quantity_wanted(qty_wanted, expected_value, expected_errors):
    typed_value, errors = validate_quantity_wanted(qty_wanted)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("shopping_list_id, expected_value, expected_errors", [
    ("1", 1, []),
    ("", None, [SHOPPING_LIST_ID_REQUIRED]),
    ("abc", None, [SHOPPING_LIST_ID_INVALID]),
])
def test_validate_shopping_list_id(shopping_list_id, expected_value, expected_errors):
    typed_value, errors = validate_shopping_list_id(shopping_list_id)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"product_id": "1", "shopping_list_id": "2", "quantity_wanted": "3"},
        {"product_id": 1, "shopping_list_id": 2, "quantity_wanted": 3},
        {}
    ),
    (
        {"product_id": "abc", "shopping_list_id": "", "quantity_wanted": "-5"},
        {},
        {
            "product_id": [PRODUCT_ID_INVALID],
            "shopping_list_id": [SHOPPING_LIST_ID_REQUIRED],
            "quantity_wanted": [QUANTITY_WANTED_POSITIVE]
        }
    )
])
def test_validate_shopping_list_item(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_shopping_list_item(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors


# NOTE: Currently only has 'name' field. Will flesh out
@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    ({"name": "x" * 300}, {}, {"name": [SHOPPING_LIST_NAME_TOO_LONG]}),
    ({"name": "Groceries"}, {"name": "Groceries"}, {}),
])
def test_validate_shopping_list(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_shopping_list(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors