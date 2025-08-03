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

    # Ensure ValueError is raised
    with pytest.raises(ValueError) as excinfo:
        validate_product_data(incomplete_data)
    
    assert "Product name is required" in str(excinfo.value)


def test_add_transaction_requires_product(logged_in_user):
    with pytest.raises(ValueError, match="Product must be provided for transaction."):
        grocery_repo.add_transaction(db_session, None, logged_in_user.id, price="2.50", quantity=1)