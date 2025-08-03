# Keep tests here to stuff like custom methods within models themselves?

from app.modules.groceries.models import Transaction
from app.core.database import db_session

def test_transaction_string_representation(sample_product, logged_in_user):
    transaction = Transaction(
        product_id=sample_product.id,
        price_at_scan=4.99, 
        quantity=2,
        user_id=logged_in_user.id
    )
    db_session.add(transaction)
    db_session.flush()

    expected = f"Transaction:{transaction.id}: 2x Test Product @ 4.99"
    assert str(transaction) == expected