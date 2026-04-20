
from app.modules.groceries.repository import TransactionRepository
from app._infra.database import db_session

def test_get_all_transactions_query_count(app, logged_in_user, query_counter):
    session = db_session()
    repo = TransactionRepository(session, logged_in_user["id"])

    ## create some test data..

    with query_counter(session, expected=1):
        transactions = repo.get_all()
        # access relationship to prove it's eager-loaded
        names = [t.product.name for t in transactions]

def test_get_all_transactions_eager_loads_product(app, sample_transactions, query_counter):
    session = db_session()
    repo = TransactionRepository(session, sample_transactions[0].user_id)

    with query_counter(session, expected=1):
        transactions = repo.get_all()
        names = [t.product.name for t in transactions]

    assert len(transactions) == 2
    assert "Apples" in names
