# Holds fixtures & test config, automatically loaded by pytest (import not required)

import os
import subprocess
import time

import pytest
from app import create_app
from app.core.database import db_session, get_engine
from app.modules.groceries.models import Product
from app.utils.database.db_utils import delete_all_db_data
from sqlalchemy import text


# Ensure PostgreSQL container is running before tests start
# TODO: Needed/used?
@pytest.fixture(scope="session", autouse=True)
def ensure_docker_postgres():

    # Check if already running
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", "name=vesper-db-dev"],
        capture_output=True, text=True
    )

    if not result.stdout.strip():
        print("Starting vesper-db-dev container...")
        subprocess.run(["docker", "start", "vesper-db-dev"])
        time.sleep(3) # Let it initialize

# Create app once & use it for all tests
@pytest.fixture(scope="session")
def app():
    # Tell Alembic which DB to use
    os.environ['APP_ENV'] = 'testing'
    app = create_app('testing')  # Pass in our TestConfig
    yield app

# Ensure we have a user with id=1 (user.id is a Foreign Key for all other models)
@pytest.fixture(scope="session", autouse=True)
def setup_test_user(app):
    engine = get_engine(app.config)

    with engine.begin() as conn:
        # Create user (use ON CONFLICT to handle if we already have a user)
        conn.execute(
            # Note: need to put user in quotes since it's a reserved keyword in PostgreSQL
            text("""INSERT INTO "user" (id, username) VALUES (1, 'testuser') ON CONFLICT (id) DO NOTHING""")
        )

    yield

# Fixture to clear all table data between tests
# Necessary now that tests and app share the same session via monkeypatching
@pytest.fixture(autouse=True)
def clear_tables(app):
    engine = get_engine(app.config)

    # Clear data before each test runs & reset sequence IDs
    delete_all_db_data(engine, reset_sequences=True)
    # Remove any hanging sessions
    db_session.remove()
    yield # Run the test

    # Clean up sessions after test
    db_session.remove()

# Get engine from app
@pytest.fixture(scope="session")
def engine(app):
    return get_engine(app.config)

# ## REMOVE?
# # Fixture to cleanup session (replaces db_session we had before)
# @pytest.fixture(autouse=True)
# def cleanup_session():
#     yield
#     db_session.remove()

# monkeypatches db_session() to use our test session
@pytest.fixture(autouse=True)
def patch_db_session(monkeypatch):
    from app.core.database import \
        db_session as \
        global_session  # Imports scoped session factory and renames it to global_session

    # lambda *_: global_session() creates a function that takes any arguments ("*_" = "ignore whatever args are passed")
    #       and returns global_session() which calls our scoped session
    # This makes all imports of db_session use our test database
    monkeypatch.setattr("app.core.database.db_session", lambda *_: global_session())

# Fake browser to test routes (lets us send requests from a fake browser/client)
@pytest.fixture
def client(app):
    return app.test_client()

# Basic sanity test
def test_postgresql_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1

# Product fixture for Transaction tests
@pytest.fixture
def sample_product():
    product = Product(
        product_name="Test Product",
        category="Test Product Category",
        barcode="123456",
        net_weight=200,
        unit_type="g",
        calories_per_100g=150
    )
    db_session.add(product)
    db_session.flush()
    return product