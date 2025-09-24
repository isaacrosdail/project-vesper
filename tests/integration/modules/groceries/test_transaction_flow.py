from app.core.database import db_session, database_connection

def test_add_transaction_submission_creates_transaction(client):
    # Create product
    with database_connection() as session:
        from app.modules.groceries.models import Product
        product = Product(
            barcode="55555",
            product_name="Transaction Product",
            category="Test Category",
            net_weight=0.8,
            unit_type="g",
            calories_per_100g=100
        )
        session.add(product) # Objects added with session.add() are immediately visible to queries in the same session
        # ie, our product query as part of our post below

        # Test endpoint (POST)
        # NOTE: client.post creates its OWN session (Session B) internally
        # But Session B can see Session A's changes changes in db?
        # After Session B commits, Session A can see the new transaction
        response = client.post("/groceries/transactions", data={
            "barcode": product.barcode,
            "price_at_scan": "4.20",
            "quantity": "1",
            "action": "submit"
        })
        assert response.status_code == 302 # Expect redirect

        # Verify transaction was created
        from app.modules.groceries.models import Transaction
        transaction = session.query(Transaction).first()
        assert transaction is not None
        assert transaction.quantity == 1
        assert transaction.product.product_name == "Transaction Product"