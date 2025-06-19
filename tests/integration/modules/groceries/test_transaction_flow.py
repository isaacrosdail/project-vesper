from app.core.database import db_session

def test_add_transaction_submission_creates_transaction(client):
    # Ensure product exists
    from app.modules.groceries.models import Product
    product = Product(
        barcode="55555",
        product_name="Transaction Product",
        category="Test Category",
        net_weight=0.8,
        unit_type="g",
        calories_per_100g=100
    )
    
    db_session.add(product)
    db_session.commit() # Can't use flush here due to client.post below
    # Since Flask treats that as a new transaction under the hood (separate request context)
    # it's technically in its own session regardless, hence the commit

    # POST transaction data
    response = client.post("/groceries/transactions/add", data={
        "barcode": product.barcode,
        "price_at_scan": "4.20",
        "quantity": "1",
        "action": "submit"
    })
    assert response.status_code == 302 # Expect redirect

    # Confirm transaction indeed exists
    from app.modules.groceries.models import Transaction
    transaction = db_session.query(Transaction).first()
    assert transaction is not None
    assert transaction.quantity == 1
    assert transaction.product.product_name == "Transaction Product"