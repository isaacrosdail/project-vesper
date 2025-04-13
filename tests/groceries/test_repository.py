from app.modules.groceries.models import Product, Transaction
from app.modules.groceries.repository import add_product, add_transaction, lookup_barcode, get_all_products, get_all_transactions
from decimal import Decimal
import pytest

# region lookup_barcode
# Return a Product if barcode exists, None if barcode doesn't exist
def test_lookup_barcode_found(db_session):
    print("Test started...")
    product_data = {
        "barcode": "1234567",
        "product_name": "Test Product",
        "price": Decimal("5.99"),
        "net_weight": 200
    }
    
    add_product(db_session, **product_data)
    db_session.commit()

    result = lookup_barcode(db_session, "1234567")

    assert result is not None
    assert isinstance(result, Product)
    assert result.product_name == "Test Product"

def test_lookup_barcode_not_found(db_session):
    result = lookup_barcode(db_session, "9999999")
    assert result is None
# endregion

# region get_all_products

def test_get_all_products_empty(db_session):
    products = get_all_products(db_session)
    assert products == []

def test_get_all_products_with_entries(db_session):
    add_product(db_session, barcode="123", product_name="Milk", price="1.50", net_weight="20.0")
    db_session.commit()

    products = get_all_products(db_session)
    assert len(products) == 1
    assert products[0].product_name == "Milk"

# endregion

# region get_all_transactions

def test_get_all_transactions_empty(db_session):
    transactions = get_all_transactions(db_session)
    assert transactions == []

def test_get_all_transactions_existing_product(db_session):
    product_data = {
        "barcode": "1234567",
        "product_name": "Test Product",
        "price": "3.50",
        "net_weight": "0.5"
    }

    add_product(db_session, **product_data)
    db_session.commit()

    product = lookup_barcode(db_session, "1234567")

    add_transaction(
        db_session,
        product,
        price="3.50",
        quantity=2
    )
    db_session.commit()

    transactions = get_all_transactions(db_session)
    assert len(transactions) == 1
    assert transactions[0].quantity == 2
    assert transactions[0].product.product_name == "Test Product"

# Test to ensure it works after session close?
def test_get_all_transactions_ensure_joinedload(db_session):
    add_product(db_session,
        barcode="111",
        product_name="PostSession Item",
        price="2.00",
        net_weight="0.3"
    )
    db_session.commit()

    product = lookup_barcode(db_session, "111")
    add_transaction(
        db_session,
        product,
        price="2.00",
        quantity=1
    )
    db_session.commit()

    transactions = get_all_transactions(db_session)
    db_session.close() # simulate session teardown

    # Won't work unless joinedload is present
    assert transactions[0].product.product_name == "PostSession Item"

# region add_product
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

# endregion

