
import pytest

from app._infra.database import db_session
from app.modules.groceries.models import (
    Product,
    ProductCategoryEnum,
    Transaction,
    UnitEnum,
)


@pytest.fixture
def sample_products(logged_in_user):
    session = db_session()

    products = [
        Product(user_id=logged_in_user.id, name="Apples", category=ProductCategoryEnum.FRUITS, net_weight=500, unit_type=UnitEnum.G),
        Product(user_id=logged_in_user.id, name="Bread", category=ProductCategoryEnum.GRAINS, net_weight=700, unit_type=UnitEnum.G),
    ]
    session.add_all(products)
    session.flush()
    return products


@pytest.fixture
def sample_transactions(logged_in_user, sample_products):
    session = db_session()

    transactions = [
        Transaction(user_id=logged_in_user.id, product_id=sample_products[0].id, price_at_scan=3.50, quantity=2),
        Transaction(user_id=logged_in_user.id, product_id=sample_products[1].id, price_at_scan=4.00, quantity=1),
    ]
    session.add_all(transactions)
    session.flush()
    return transactions
