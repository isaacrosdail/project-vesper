from modules.groceries.models import Product, Transaction
from modules.groceries.repository import add_product, lookup_barcode
from decimal import Decimal
import pytest

# region Lookup Barcode Tests
# Return a Product if barcode exists, None if barcode doesn't exist
def test_lookup_barcode_found(db_session):
    product_data = {
        "barcode": "1234567",
        "product_name": "Test Product",
        "price": Decimal("5.99"),
        "net_weight": 200
    }
    
    add_product(db_session, **product_data)
    result = lookup_barcode(db_session, "1234567")

    assert result is not None
    assert isinstance(result, Product)
    assert result.product_name == "Test Product"

def test_lookup_barcode_not_found(db_session):
    result = lookup_barcode(db_session, "9999999")
    assert result is None
# endregion

# Happy path test
def test_add_product(db_session):
    product_data = {
        "barcode": "1234567",
        "product_name":"Test Product",
        "price": Decimal("5.99"),
        "net_weight": 200
    }

    add_product(db_session, **product_data)

    # Query DB to verify
    result = db_session.query(Product).filter_by(barcode=product_data["barcode"]).first()

    assert result is not None
    assert result.product_name == product_data["product_name"]
    assert result.price == product_data["price"]
    assert result.net_weight == product_data["net_weight"]

# Missing data test
def test_add_product_missing_data_raises_error(db_session):
    incomplete_data = {
        "barcode":"1234567",
        "price": Decimal("5.99"),
        "net_weight": 200
    }

    # Ensure ValueError is raised
    with pytest.raises(ValueError) as excinfo:
        add_product(db_session, **incomplete_data)
    
    assert "Product name is required" in str(excinfo.value)

# Invalid range for price
def test_add_product_invalid_range(db_session):
    invalid_range_data = {
        "barcode":"1234567",
        "product_name":"Test Product2",
        "price": "-12.99",
        "net_weight": 200
    }

    # Ensure ValueError is raised
    with pytest.raises(ValueError) as excinfo:
        add_product(db_session, **invalid_range_data)

    assert "Price must be provided and non-negative." in str(excinfo.value)