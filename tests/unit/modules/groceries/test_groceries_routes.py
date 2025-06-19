from app.core.database import db_session


def test_groceries_dashboard(client):
    response = client.get("/groceries/")
    assert response.status_code == 200
    # assert b"Groceries" in response.data ADD THIS CHECK WHEN WE ADD LANGUAGE TOGGLE TO EN DE

def test_add_product_page_loads(client):
    response = client.get("/groceries/products/add")
    assert response.status_code == 200
    assert "Add new product" in response.get_data(as_text=True)

def test_add_product_submission_creates_product(client):
    data = {
        "barcode": "1234567890",
        "product_name": "Test Product",
        "category": "Test Category",
        "net_weight": 15,
        "unit_type": "g",
        "calories_per_100g": 100
    }

    response = client.post("/groceries/products/add", data=data)
    assert response.status_code == 302 # Redirect to dashboard

    # Confirm product is in DB
    from app.modules.groceries.models import Product
    product = db_session.query(Product).filter_by(barcode="1234567890").first()
    assert product is not None
    assert product.product_name == "Test Product"