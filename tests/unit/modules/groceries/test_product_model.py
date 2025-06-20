
from app.modules.groceries.models import Product

def test_product_creation():
    product = Product(
        barcode="12345",
        product_name="Test Chips",
        category="Snacks",
        net_weight=100,
        unit_type="g"
    )
    assert product.barcode == "12345"
    assert product.product_name == "Test Chips"

def test_product_string_representation():
    product = Product(product_name="Salsa", barcode="12345")
    assert str(product) == "Salsa (12345)"