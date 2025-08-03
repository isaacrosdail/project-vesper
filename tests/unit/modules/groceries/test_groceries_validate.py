from decimal import Decimal

import pytest

from app.core.database import db_session
from app.modules.groceries import repository as grocery_repo
from app.modules.groceries.models import Product, Transaction
from app.modules.groceries.validate import validate_product_data, validate_transaction_data

# Missing data test
def test_add_product_missing_data_raises_error():
    incomplete_data = {
        "barcode":"1234567",
        "price": Decimal("5.99"),
        "net_weight": 200
    }

    errors = validate_product_data(incomplete_data)
    # # Ensure ValueError is raised
    # with pytest.raises(ValueError) as excinfo:
    #     validate_product_data(incomplete_data)
    # assert "Product name is required" in str(excinfo.value)
    assert len(errors) == 3 # (missing product_name, category, unit_type)

def test_add_transaction_requires_product():
    #with pytest.raises(ValueError, match="Product must be provided for transaction."):
    transaction_data = {
        "product_name"
    }
    validate_transaction_data(db_session, None, price_at_scan="2.50", quantity=1)