from modules.groceries.models import add_product, Product
from decimal import Decimal
import pytest

def test_add_product(db_session):
    barcode="1234567"
    product_data = {
        "product_name":"Test Product",
        "price_at_scan": Decimal("5.99"),
        "net_weight": 200
    }

    add_product(db_session, barcode, **product_data)

    # Query DB to verify
    result = db_session.query(Product).filter_by(barcode=barcode).first()

    assert result is not None
    assert result.product_name == product_data["product_name"]
    assert result.price == product_data["price_at_scan"]
    assert result.net_weight == product_data["net_weight"]