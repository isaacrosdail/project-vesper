import pytest
from app.modules.groceries.validators import *
from app.modules.groceries.models import Unit

# Error message constants for groceries

@pytest.mark.parametrize("product_data", [
    {"name": "Milk", "barcode": "123456", "net_weight": "1.0", "unit_type": "l"},
    {"name": "Bread", "barcode": "789", "net_weight": "500", "unit_type": "g", "category": "grain", "calories_per_100g": "250"},
    {"name": "a" * 100, "barcode": "b" * 16, "net_weight": "1", "unit_type": "kg"},
    {"name": "Cheese", "barcode": "456", "net_weight": "0.5", "unit_type": "lb"},
])
def test_validate_product_success(product_data):
    assert validate_product(product_data) == []

@pytest.mark.parametrize("product_data,expected_errors", [
    # Missing required fields
    ({"barcode": "123", "net_weight": "1", "unit_type": "g"}, [PRODUCT_NAME_REQUIRED]),
    ({"name": "Milk", "net_weight": "1", "unit_type": "g"}, [BARCODE_REQUIRED]),
    ({"name": "Milk", "barcode": "123", "unit_type": "g"}, [NET_WEIGHT_REQUIRED]),
    ({"name": "Milk", "barcode": "123", "net_weight": "1"}, [UNIT_TYPE_REQUIRED]),
    
    # Length violations
    ({"name": "a" * 101, "barcode": "123", "net_weight": "1", "unit_type": "g"}, [PRODUCT_NAME_LENGTH]),
    ({"name": "Milk", "barcode": "a" * 65, "net_weight": "1", "unit_type": "g"}, [BARCODE_LENGTH]),
    
    # Invalid numeric values
    ({"name": "Milk", "barcode": "123", "net_weight": "0", "unit_type": "g"}, [NET_WEIGHT_POSITIVE]),
    ({"name": "Milk", "barcode": "123", "net_weight": "-1", "unit_type": "g"}, [NET_WEIGHT_POSITIVE]),
    ({"name": "Milk", "barcode": "123", "net_weight": "not_a_number", "unit_type": "g"}, [NET_WEIGHT_INVALID]),
    
    # Invalid enum
    ({"name": "Milk", "barcode": "123", "net_weight": "1", "unit_type": "invalid_unit"}, [UNIT_TYPE_INVALID]),
])
def test_validate_product_errors(product_data, expected_errors):
    errors = validate_product(product_data)
    assert set(errors) == set(expected_errors) # using set to enforce "validator must return _only_ the errors we defined, but order doesn't matter"


@pytest.mark.parametrize("transaction_data", [
    # Basic valid transaction
    {"price_at_scan": "3.99", "quantity": "2"},
    # With product_id
    {"price_at_scan": "5.50", "quantity": "1", "product_id": "123"},
    # Edge cases
    {"price_at_scan": "0.01", "quantity": "1"},  # Very small price
    {"price_at_scan": "999.99", "quantity": "100"},  # Large values
    # Different number formats
    {"price_at_scan": "10", "quantity": "5"},  # Integer as string
    {"price_at_scan": "2.5", "quantity": "3"},  # Float as string
])
def test_validate_transaction_success(transaction_data):
    assert validate_transaction(transaction_data) == []

@pytest.mark.parametrize("transaction_data,expected_errors", [
    # Missing required fields
    ({"quantity": "2"}, [PRICE_REQUIRED]),
    ({"price_at_scan": "3.99"}, [QUANTITY_REQUIRED]),
    
    # Invalid price values
    ({"price_at_scan": "-1.00", "quantity": "2"}, [PRICE_NEGATIVE]),
    ({"price_at_scan": "not_a_price", "quantity": "2"}, [PRICE_INVALID]),
    ({"price_at_scan": "", "quantity": "2"}, [PRICE_REQUIRED]),
    
    # Invalid quantity values
    ({"price_at_scan": "3.99", "quantity": "0"}, [QUANTITY_POSITIVE]),
    ({"price_at_scan": "3.99", "quantity": "-1"}, [QUANTITY_POSITIVE]),
    ({"price_at_scan": "3.99", "quantity": "2.5"}, [QUANTITY_INVALID]),  # Should be whole number
    ({"price_at_scan": "3.99", "quantity": "not_a_number"}, [QUANTITY_INVALID]),
    
    # Invalid product_id
    #({"price_at_scan": "3.99", "quantity": "2", "product_id": "not_a_number"}, [PRODUCT_ID_INVALID]),
    
    # Multiple errors
    ({"price_at_scan": "", "quantity": ""}, [PRICE_REQUIRED, QUANTITY_REQUIRED]),
])
def test_validate_transaction_errors(transaction_data, expected_errors):
    errors = validate_transaction(transaction_data)
    assert set(errors) == set(expected_errors)

@pytest.mark.parametrize("shopping_list_data", [
    {},  # Empty data (name is optional with default)
    {"name": "Weekly Shopping"},
    {"name": "a" * 100},  # Max length
    {"name": ""},  # Empty name (should be valid)
])
def test_validate_shopping_list_success(shopping_list_data):
    assert validate_shopping_list(shopping_list_data) == []

@pytest.mark.parametrize("shopping_list_data,expected_errors", [
    # Only one way to fail - name too long
    ({"name": "a" * 101}, [SHOPPING_LIST_NAME_LENGTH]),
])
def test_validate_shopping_list_errors(shopping_list_data, expected_errors):
    errors = validate_shopping_list(shopping_list_data)
    assert set(errors) == set(expected_errors)


@pytest.mark.parametrize("item_data", [
    # Basic valid item
    {"quantity_wanted": "1", "product_id": "123"},
    # With shopping list ID
    {"quantity_wanted": "5", "product_id": "456", "shopping_list_id": "789"},
    # Edge cases
    {"quantity_wanted": "100", "product_id": "1"},  # Large quantity
])
def test_validate_shopping_list_item_success(item_data):
    assert validate_shopping_list_item(item_data) == []

@pytest.mark.parametrize("item_data,expected_errors", [
    # Missing required fields
    ({"product_id": "123"}, [QUANTITY_WANTED_REQUIRED]),
    ({"quantity_wanted": "1"}, [PRODUCT_REQUIRED]),
    
    # Invalid quantity values
    ({"quantity_wanted": "0", "product_id": "123"}, [QUANTITY_WANTED_POSITIVE]),
    ({"quantity_wanted": "-1", "product_id": "123"}, [QUANTITY_WANTED_POSITIVE]),
    ({"quantity_wanted": "2.5", "product_id": "123"}, [QUANTITY_WANTED_INVALID]),  # Should be whole number
    ({"quantity_wanted": "not_a_number", "product_id": "123"}, [QUANTITY_WANTED_INVALID]),
    
    # Invalid foreign keys
    ({"quantity_wanted": "1", "product_id": "not_a_number"}, [PRODUCT_ID_INVALID]),
    ({"quantity_wanted": "1", "product_id": "123", "shopping_list_id": "not_a_number"}, [SHOPPING_LIST_ID_INVALID]),
    
    # Multiple errors
    #({"quantity_wanted": "", "product_id": ""}, [QUANTITY_WANTED_REQUIRED, PRODUCT_REQUIRED]),
])
def test_validate_shopping_list_item_errors(item_data, expected_errors):
    errors = validate_shopping_list_item(item_data)
    assert set(errors) == set(expected_errors)