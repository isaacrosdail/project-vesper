"""
Houses fixtures & test config, automatically loaded by pytest.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from contextlib import contextmanager


import pytest
from flask_login import login_user
from sqlalchemy import text, event

from app import create_app
from app._infra.database import db_session
from app.modules.auth.models import User
from app.shared.models import Pillar
from app.shared.database.helpers import delete_all_db_data


class AuthActions():
    def __init__(self, client):
        self.client = client
    
    def login(self, username='Test_username', password='password123'):
        # This sets a session cookie (telling Flask-Login we're logged in)
        return self.client.post('/login', data={ 
            'username': username, 
            'password': password
        })

# Drafting authenticated_client fixture
@pytest.fixture
def authenticated_client(client, auth, logged_in_user):
    # 1. Pass in client
    # 2. Do the login POST part => this gives us our "logged in" session cookie in the same HTTP context
    # ..which is what Flask-Login is looking for to ensure we're authenticated
    # auth.login(logged_in_user.username, 'password123')
    # return client # <= client now has session cookie attached
    # auth.login(logged_in_user["username"], logged_in_user["password"])
    # return client
    resp = auth.login(
        logged_in_user["username"],
        logged_in_user["password"]
    )
    assert resp.status_code in (200, 302)  # depending on your login route
    return client


# Create app once & use it for all tests
@pytest.fixture(scope="session")
def app():
    app = create_app('testing')  # Pass in our TestConfig
    with app.app_context():
        from app._infra.db_base import Base
        # prevent objs being expired after commit
        db_session.remove()
        db_session.configure(expire_on_commit=False)
        Base.metadata.create_all(bind=db_session.get_bind())

        yield app
        Base.metadata.drop_all(bind=db_session.get_bind())


# Fixture to give us a logged in user to test with
@pytest.fixture
def logged_in_user(app): # add clear_tables as dependency to ensure it runs before this?
    """Creates a logged-in user for testing authenticated routes."""
    # Creates fake HTTP request context for testing
    # Makes Flask think it's handling a real web request
    # Enables things like request, session, current_user
    # with app.test_request_context():
    #     user = User(
    #         username="Test_username", 
    #         name="Test_user", 
    #         role='user'
    #     )
    #     user.hash_password('password123')
    #     db_session.add(user)
    #     db_session.flush()

    #     pillars = [
    #         Pillar(name="Health", user_id=user.id),
    #         Pillar(name="Career", user_id=user.id),
    #         Pillar(name="Purpose", user_id=user.id),
    #         Pillar(name="Rest", user_id=user.id),
    #         Pillar(name="Relationships", user_id=user.id),
    #     ]
    #     db_session.add_all(pillars)
    #     db_session.commit()

    #     user_id = user.id
    #     username = user.username

    # return {"id": user_id, "username": username, "password": "password123"}

    user = User(
        username="Test_username",
        name="Test_user",
        role='user'
    )
    user.hash_password('password123')
    db_session.add(user)
    db_session.flush()

    pillars = [
        Pillar(name="Health", user_id=user.id),
        Pillar(name="Career", user_id=user.id),
    ]
    db_session.add_all(pillars)
    db_session.commit()

    return {
        "id": user.id,
        "username": user.username,
        "password": "password123"
    }


# Fixture to clear all table data between tests
# Necessary now that tests and app share the same session via monkeypatching
@pytest.fixture(autouse=True)
def clear_tables(app):
    yield

    # Cleanup SQLAlchemy-side
    db_session.rollback()   # rollback pending
    db_session.expire_all() # clear identity map (session dies when requests end, hence why I never had this SQLAlchemy identity issue before)

    delete_all_db_data(db_session, reset_sequences=True, include_users=True)
    db_session.commit()
    #yield

# # monkeypatches db_session() to use our test session
# @pytest.fixture(autouse=True)
# def patch_db_session(monkeypatch):
#     from app._infra.database import \
#         db_session as \
#         global_session  # Imports scoped session factory and renames it to global_session

#     # lambda *_: global_session() creates a function that takes any arguments ("*_" = "ignore whatever args are passed")
#     #       and returns global_session() which calls our scoped session
#     # This makes all imports of db_session use our test database
#     monkeypatch.setattr("app._infra.database.db_session", lambda *_: global_session())

@pytest.fixture(autouse=True)
def patch_db_connection(monkeypatch):
    from contextlib import contextmanager

    @contextmanager
    def test_database_connection():
        session = db_session()
        try:
            yield session
            session.flush()  # flush but don't commit — let clear_tables handle cleanup
        except Exception:
            session.rollback()
            raise
        # NO session.close() — keep it alive for Flask-Login

    monkeypatch.setattr("app._infra.database.database_connection", test_database_connection)
    monkeypatch.setattr("app.shared.decorators.database_connection", test_database_connection)

# Fake browser to test routes (lets us send requests from a fake browser/client)
@pytest.fixture
def client(app):
    return app.test_client()

# Wrapper around test_client that adds convenient authentication methods
@pytest.fixture
def auth(client):
    return AuthActions(client)

# Basic sanity test
def test_postgresql_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


# TODO: Study!!
@pytest.fixture
def query_counter(app):
    @contextmanager
    def count_queries(session: Session, expected: int):
        queries = []
        engine = session.get_bind()

        # before_cursor_execute event (from SQLAlchemy ofc) fires before every
        # SQL statement and passes all of these:
        def log_query(conn, cursor, statement, parameters, context, executemany):
            queries.append(statement)

        event.listen(engine, "before_cursor_execute", log_query)
        yield queries
        event.remove(engine, "before_cursor_execute", log_query)

        assert len(queries) == expected, (
            f"Expected {expected} queries, got {len(queries)}:\n"
            + "\n.join(queries)"
        )

    return count_queries


@pytest.fixture
def sample_products(logged_in_user):
    session = db_session()
    from app.modules.groceries.models import Product

    products = [
        Product(user_id=logged_in_user["id"], name="Apples", category="fruits", net_weight=500, unit_type="g"),
        Product(user_id=logged_in_user["id"], name="Bread", category="grains", net_weight=700, unit_type="g"),
    ]
    session.add_all(products)
    session.flush()
    return products


@pytest.fixture
def sample_transactions(logged_in_user, sample_products):
    session = db_session()
    from app.modules.groceries.models import Transaction

    transactions = [
        Transaction(user_id=logged_in_user["id"], product_id=sample_products[0].id, price_at_scan=3.50, quantity=2),
        Transaction(user_id=logged_in_user["id"], product_id=sample_products[1].id, price_at_scan=4.00, quantity=1),
    ]
    session.add_all(transactions)
    session.flush()
    return transactions

