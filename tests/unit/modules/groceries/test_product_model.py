# Keep tests here to stuff like custom methods within models themselves?

from app.modules.groceries.models import Product


def test_product_string_representation():
    product = Product(product_name="Salsa", barcode="12345")
    assert str(product) == "Salsa (12345)"