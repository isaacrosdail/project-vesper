from decimal import Decimal


from app._infra.database import db_session
from app.modules.groceries.validators import validate_product_data, validate_transaction_data

# Missing data test
def test_add_product_missing_data_raises_error():
    # ARRANGE
    incomplete_data = {
        "barcode":"1234567",
        "price": Decimal("5.99"),
        "net_weight": 200
    }

    # ACT
    errors = validate_product_data(incomplete_data)

    # ASSERT
    assert len(errors) == 3 # (missing product_name, category, unit_type)

# TODO: Flesh out validation function
def test_add_transaction_requires_product():
    #with pytest.raises(ValueError, match="Product must be provided for transaction."):
    transaction_data = {
        "product_name"
    }
    validate_transaction_data(db_session, None, price_at_scan="2.50", quantity=1)