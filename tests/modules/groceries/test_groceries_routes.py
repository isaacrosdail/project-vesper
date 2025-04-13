from sqlalchemy.orm import joinedload



def test_groceries_dashboard(client):
    response = client.get("/groceries/")
    assert response.status_code == 200
    # assert b"Groceries" in response.data ADD THIS CHECK WHEN WE ADD LANGUAGE TOGGLE TO EN DE

def test_add_product_page_loads(client):
    response = client.get("/groceries/add_product")
    assert response.status_code == 200
    assert "Add new product" in response.get_data(as_text=True)

def test_add_product_submission_creates_product(client, db_session):
    data = {
        "barcode": "1234567890",
        "product_name": "Test Product",
        "price": "3.99",
        "net_weight": "15"
    }

    response = client.post("/groceries/add_product", data=data)
    assert response.status_code == 302 # Redirect to dashboard

    # Confirm product is in DB
    from app.modules.groceries.models import Product
    product = db_session.query(Product).filter_by(barcode="1234567890").first()
    assert product is not None
    assert product.product_name == "Test Product"

def test_add_transaction_submission_creates_transaction(client, db_session):
    # Ensure product exists
    from app.modules.groceries.models import Product
    product = Product(
        barcode="55555",
        product_name="Transaction Product",
        price=4.20,
        net_weight=0.8
    )
    db_session.add(product)
    db_session.commit()

    # POST transaction data
    response = client.post("/groceries/add_transaction", data={
        "barcode": product.barcode,
        "price": "4.20",
        "quantity": "1",
        "action": "submit"
    })
    assert response.status_code == 302 # Expect redirect

    # Confirm transaction indeed exists
    from app.modules.groceries.models import Transaction
    print("Product name:", product.product_name)
    transaction = db_session.query(Transaction).first()
    print("Transaction name:", transaction.product.product_name)
    assert transaction is not None
    assert transaction.quantity == 1