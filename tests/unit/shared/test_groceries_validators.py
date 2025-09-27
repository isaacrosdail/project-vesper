import pytest

from app.modules.groceries.validators import *
from app.modules.groceries.constants import *
from app.modules.groceries.models import UnitEnum


def test_unit_type_required():
    assert validate_unit_type("") == [UNIT_TYPE_REQUIRED]
    assert validate_unit_type(None) == [UNIT_TYPE_REQUIRED]


@pytest.mark.parametrize("valid_value", [unit.value for unit in UnitEnum])
def test_unit_type_valid(valid_value):
    assert validate_unit_type(valid_value) == []


def test_validate_shopping_list_name_too_long():
    data = {"name": "x" * 300}
    assert validate_shopping_list(data) == {"name": [SHOPPING_LIST_NAME_TOO_LONG]}

def test_validate_shopping_list_name_valid():
    data = {"name": "Groceries"}
    assert validate_shopping_list(data) == {}



@pytest.mark.parametrize("qty_wanted, expected", [
    ("", [QUANTITY_WANTED_REQUIRED]),
    ("0", [QUANTITY_WANTED_POSITIVE]),
    ("abc", [QUANTITY_WANTED_INVALID]),
    ("2", [])
])
def test_validate_quantity_wanted(qty_wanted, expected):
    assert validate_quantity_wanted(qty_wanted) == expected

@pytest.mark.parametrize("product_id, expected", [
    ("", [PRODUCT_ID_REQUIRED]),
    ("abc", [PRODUCT_ID_INVALID]),
    ("1", []),
])
def test_validate_product_id(product_id, expected):
    assert validate_product_id(product_id) == expected


@pytest.mark.parametrize("shopping_list_id, expected", [
    ("", [SHOPPING_LIST_ID_REQUIRED]),
    ("abc", [SHOPPING_LIST_ID_INVALID]),
    ("1", []),
])
def test_validate_shopping_list_id(shopping_list_id, expected):
    assert validate_shopping_list_id(shopping_list_id) == expected


@pytest.mark.parametrize("data, expected", [
    ({"product_id": "1", "shopping_list_id": "2", "quantity_wanted": "3"}, {})
])
def test_validate_shopping_list_item_success(data, expected):
    assert validate_shopping_list_item(data) == expected

@pytest.mark.parametrize("data, expected", [
    ({"product_id": "abc", "shopping_list_id": "", "quantity_wanted": "-5"},
     {
        "product_id": [PRODUCT_ID_INVALID],
        "shopping_list_id": [SHOPPING_LIST_ID_REQUIRED],
        "quantity_wanted": [QUANTITY_WANTED_POSITIVE]
     })
])
def test_validate_shopping_list_item_errors(data, expected):
    errors = validate_shopping_list_item(data)
    assert errors == expected


@pytest.mark.parametrize("product_name, expected", [
    ("", [PRODUCT_NAME_REQUIRED]),
    ("a" * 100, [PRODUCT_NAME_TOO_LONG]),
    ("Apples", [])
])
def test_validate_product_name(product_name, expected):
    assert validate_product_name(product_name) == expected

@pytest.mark.parametrize("barcode, expected", [
    ("", [BARCODE_REQUIRED]),
    ("invalid!!", [BARCODE_INVALID]),
    ("123456789012", []),
])
def test_validate_barcode(barcode, expected):
    assert validate_barcode(barcode) == expected


@pytest.mark.parametrize("net_weight, expected", [
    ("", [NET_WEIGHT_REQUIRED]),
    ("abc", [NET_WEIGHT_INVALID]),
    ("-5.00", [NET_WEIGHT_POSITIVE]),
    ("12.3456", [NET_WEIGHT_INVALID]),
    ("100.00", []),
])
def test_validate_net_weight(net_weight, expected):
    assert validate_net_weight(net_weight) == expected


@pytest.mark.parametrize("unit_type, expected", [
    ("", [UNIT_TYPE_REQUIRED]),
    ("INVALID", [UNIT_TYPE_INVALID]),
    ("G", []),
])
def test_validate_unit_type(unit_type, expected):
    assert validate_unit_type(unit_type) == expected


@pytest.mark.parametrize("category, expected", [
    ("", [CATEGORY_REQUIRED]),
    ("NOT_A_CATEGORY", [CATEGORY_INVALID]),
    ("DAIRY_EGGS", []),
])
def test_validate_category(category, expected):
    assert validate_category(category) == expected


@pytest.mark.parametrize("calories, expected", [
    ("", []),
    ("-10.00", [CALORIES_NEGATIVE]),
    ("not_a_number", [CALORIES_INVALID]),
    ("100.123", [CALORIES_INVALID]),
    ("200.50", []),
])
def test_validate_calories(calories, expected):
    assert validate_calories(calories) == expected


@pytest.mark.parametrize("price, expected", [
    ("", [PRICE_REQUIRED]),
    ("-1.00", [PRICE_NEGATIVE]),
    ("abc", [PRICE_INVALID]),
    ("1.99", [])
])
def test_validate_price(price, expected):
    assert validate_price(price) == expected

@pytest.mark.parametrize("transaction_quantity, expected", [
    ("", [QUANTITY_REQUIRED]),
    ("0", [QUANTITY_POSITIVE]),
    ("abc", [QUANTITY_INVALID]),
    ("5", [])
])
def test_validate_quantity(transaction_quantity, expected):
    assert validate_quantity(transaction_quantity) == expected

