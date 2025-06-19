from decimal import Decimal

import pytest

from app.core.database import db_session
from app.modules.groceries import repository as grocery_repo
from app.modules.groceries.models import Product, Transaction


# region lookup_barcode
# Return a Product if barcode exists, None if barcode doesn't exist
def test_lookup_barcode_found():

    product_data = {
        "barcode": "1234567",
        "product_name": "Test Product",
        "category": "Test Category",
        "net_weight": 200,
        "unit_type": "g",
        "calories_per_100g": 100

    }
    
    grocery_repo.add_product(db_session, **product_data)
    db_session.flush() # flush(), don't commit() -> Committing breaks rollback isolation

    result = grocery_repo.lookup_barcode(db_session, "1234567")

    assert result is not None
    assert isinstance(result, Product)
    assert result.product_name == "Test Product"

def test_lookup_barcode_not_found():
    result = grocery_repo.lookup_barcode(db_session, "9999999")
    assert result is None
# endregion

# region get_all_products

def test_get_all_products_empty():
    products = grocery_repo.get_all_products(db_session)
    assert products == []

def test_get_all_products_with_entries():
    product_data = {
        "barcode": "123",
        "product_name": "Milk",
        "category": "Test Category",
        "net_weight": 20,
        "unit_type": "g",
        "calories_per_100g": 100
    }
        
    grocery_repo.add_product(db_session, **product_data)
    db_session.flush()

    products = grocery_repo.get_all_products(db_session)
    assert len(products) == 1
    assert products[0].product_name == "Milk"

# endregion

# region get_all_transactions

def test_get_all_transactions_empty():
    transactions = grocery_repo.get_all_transactions(db_session)
    assert transactions == []

def test_get_all_transactions_existing_product():

    product_data = {
        "barcode": "1234567",
        "product_name": "Test Product",
        "category": "Test Category",
        "net_weight": 200,
        "unit_type": "g",
        "calories_per_100g": 100

    }

    grocery_repo.add_product(db_session, **product_data)
    
    # Use flush instead of commit
    db_session.flush()

    product = grocery_repo.lookup_barcode(db_session, "1234567")

    grocery_repo.add_transaction(
        db_session,
        product,
        price="3.50",
        quantity=2
    )
    db_session.flush() # Again, flush instead of commit

    transactions = grocery_repo.get_all_transactions(db_session)

    assert len(transactions) == 1
    assert transactions[0].quantity == 2
    assert transactions[0].product.product_name == "Test Product"

# Test to ensure it works after session close?
def test_get_all_transactions_ensure_joinedload():
    grocery_repo.add_product(db_session,
        barcode="111",
        product_name="PostSession Item",
        category="Test Category",
        price="2.00",
        net_weight="0.3",
        unit_type="g",
        calories_per_100g=100

    )
    db_session.flush() # instead of commit

    product = grocery_repo.lookup_barcode(db_session, "111")
    grocery_repo.add_transaction(
        db_session,
        product,
        price="2.00",
        quantity=1
    )
    db_session.flush() # again, instead of commit

    transactions = grocery_repo.get_all_transactions(db_session)

    # expunge_all instead of .close() here to simulate teardown without breaking rollback
    db_session.expunge_all() # simulate session teardown

    # Debug print
    print(transactions[0].__dict__)
    print(transactions[0].product.__dict__)
    # Won't work unless joinedload is present
    assert transactions[0].product.product_name == "PostSession Item"

# endregion

# region add_product
# Happy path test
def test_add_product():
    product_data = {
        "barcode": "123",
        "product_name": "Milk",
        "category": "Test Category",
        "net_weight": 20,
        "unit_type": "g",
        "calories_per_100g": 100
    }

    grocery_repo.add_product(db_session, **product_data)

    # Query DB to verify
    result = db_session.query(Product).filter_by(barcode=product_data["barcode"]).first()

    assert result is not None
    assert result.product_name == product_data["product_name"]
    assert result.category == product_data["category"]
    assert result.net_weight == product_data["net_weight"]

# Missing data test
def test_add_product_missing_data_raises_error():
    incomplete_data = {
        "barcode":"1234567",
        "price": Decimal("5.99"),
        "net_weight": 200
    }

    # Ensure ValueError is raised
    with pytest.raises(ValueError) as excinfo:
        grocery_repo.add_product(db_session, **incomplete_data)
    
    assert "Product name is required" in str(excinfo.value)

# endregion

# region add_transaction

def test_add_transaction_requires_product():
    with pytest.raises(ValueError, match="Product must be provided for transaction."):
        grocery_repo.add_transaction(db_session, None, price="2.50", quantity=1)


# endregion