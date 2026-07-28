"""
Houses fixtures & test config, automatically loaded by pytest.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app._infra.db_base import Base
from app.modules.auth.models import User
from app.modules.auth.repository import UsersRepository
from app.modules.auth.schemas import UserRegister
from app.modules.auth.service import AuthService

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from sqlalchemy.orm import Session

import pytest
from sqlalchemy import event

from app import create_app
from app._infra.database import db_session


class AuthActions:
    def __init__(self, client) -> None:
        self.client = client

    def login(self, username, password):
        return self.client.post("/login", data={
            "username": username,
            "password": password
        })

# Drafting authenticated_client fixture
@pytest.fixture
def authenticated_client(client: FlaskClient, auth, logged_in_user):
    # 1. Pass in client
    # 2. Do the login POST part => this gives us our "logged in" session cookie in the same HTTP context
    # ..which is what Flask-Login is looking for to ensure we're authenticated
    resp = auth.login(
        logged_in_user.username,
        logged_in_user.password
    )
    assert resp.status_code in (200, 302)
    return client


# Create app once & use it for all tests
@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    if "test" not in app.config["SQLALCHEMY_DATABASE_URI"]:
        pytest.exit("Aborting: not the test DB", returncode=1)
    with app.app_context():
        # prevent objs being expired after commit
        db_session.remove()
        db_session.configure(expire_on_commit=False)
        Base.metadata.create_all(bind=db_session.get_bind())

        yield app
        Base.metadata.drop_all(bind=db_session.get_bind())


@dataclass
class LoggedInUserFixture:
    id: int
    username: str
    password: str
    timezone: str
    user: User

# Fixture to give us a logged in user to test with
@pytest.fixture
def logged_in_user(app) -> LoggedInUserFixture: # add clear_tables as dependency to ensure it runs before this?
    """Creates a logged-in user for testing authenticated routes."""
    # Creates fake HTTP request context for testing
    # Makes Flask think it's handling a real web request
    # Enables things like request, session, current_user
    validated = UserRegister(
        username="Test_username",
        password="password123",
        name="testuser",
        timezone="America/Chicago",
    )
    service = AuthService(db_session(), user_repo=UsersRepository(db_session()))
    user = service.register_user(validated)
    db_session.commit()

    return LoggedInUserFixture(
        id=user.id,
        username=user.username,
        password="password123",
        timezone=user.timezone,
        user=user
    )

@pytest.fixture
def second_logged_in_user(app) -> LoggedInUserFixture:
    validated = UserRegister(
        username="SecondUsername",
        password="password456",
        name="secondtestuser",
        timezone="America/Chicago",
    )
    service = AuthService(db_session(), user_repo=UsersRepository(db_session()))
    user = service.register_user(validated)
    db_session.commit()

    return LoggedInUserFixture(
        id=user.id,
        username=user.username,
        password="password456",
        timezone=user.timezone,
        user=user
    )


# Engine bound at session start & cached forever
@pytest.fixture(scope="session")
def engine(app):
    return db_session.get_bind()

# Joining a Session into an External Transaction
## https://docs.sqlalchemy.org/en/21/orm/session_transaction.html#session-external-transaction
@pytest.fixture(autouse=True)
def db_transaction(engine):
    connection = engine.connect()
    outer = connection.begin()
    db_session.remove()  # evict sessions made under the old bind
    # create_savepoint: session.commit() becomes non-durable between tests
    db_session.configure(bind=connection, join_transaction_mode="create_savepoint")

    yield

    db_session.remove()
    db_session.configure(bind=engine) # restore?
    outer.rollback()
    connection.close()

@pytest.fixture
def session():
    return db_session()

# Fake browser to test routes
@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()

# Wrapper around test_client that adds convenient authentication methods
@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def query_counter(app):
    @contextmanager
    def count_queries(session: Session, expected: int):
        queries = []
        connection = session.get_bind()

        # before_cursor_execute event (from SQLAlchemy ofc) fires before every
        # SQL statement and passes all of these:
        def log_query(conn, cursor, statement, parameters, context, executemany):
            if not statement.startswith(("SAVEPOINT", "RELEASE SAVEPOINT", "ROLLBACK TO SAVEPOINT")):
                queries.append(statement)

        event.listen(connection, "before_cursor_execute", log_query)
        yield queries
        event.remove(connection, "before_cursor_execute", log_query)

        assert len(queries) == expected, (
            f"Expected {expected} queries, got {len(queries)}:\n"
            + "\n".join(queries)
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

