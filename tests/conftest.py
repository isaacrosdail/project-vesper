# Holds fixtures & test config, automatically loaded by pytest (import not required)

import os
import subprocess
import time

import sys

import pytest
from app import create_app
from app.core.database import db_session, get_engine
from app.modules.groceries.models import Product
from app.common.database.operations import delete_all_db_data
from sqlalchemy import text

from app.core.auth.models import User
from flask_login import login_user

class AuthActions():
    def __init__(self, client):
        self.client = client
    
    def login(self, username, password):
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
    auth.login(logged_in_user.username, 'password123')
    
    return client # <= client now has session cookie attached

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

# # Ensure we have a user with id=1 (user.id is a Foreign Key for all other models)
# @pytest.fixture(scope="session", autouse=True)
# def setup_test_user(app):
#     engine = get_engine(app.config)

#     with engine.begin() as conn:
#         # Create user (use ON CONFLICT to handle if we already have a user)
#         conn.execute(
#             # Note: need to put user in quotes since it's a reserved keyword in PostgreSQL
#             text("""INSERT INTO "user" (id, username) VALUES (1, 'testuser') ON CONFLICT (id) DO NOTHING""")
#         )
#     yield

# Fixture to give us a logged in user to test with
@pytest.fixture
def logged_in_user(app, clear_tables): # add clear_tables as dependency to ensure it runs before this?
    """Creates a logged-in user for testing authenticated routes."""
    # Creates fake HTTP request context for testing
    # Makes Flask think it's handling a real web request
    # Enables things like request, session, current_user
    with app.test_request_context():
        print(f"DEBUG logged_in_user: Session ID = {id(db_session)}")
        print(f"DEBUG logged_in_user: Session info = {db_session.info}")
        import time
        unique_username = f"Base_User_{int(time.time())}"
        # Create test user
        user = User(username=unique_username, name="Jeff", role='user')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()

        login_user(user)
        
    return user

# Fixture to clear all table data between tests
# Necessary now that tests and app share the same session via monkeypatching
@pytest.fixture(autouse=True)
def clear_tables(app):
    print(f"DEBUG clear_tables: Session ID = {id(db_session)}")

    # # Clear data before each test runs & reset sequence IDs
    # delete_all_db_data(engine, reset_sequences=True)
    delete_all_db_data(db_session, reset_sequences=True, include_users=True)
    db_session.commit()
    
    remaining = db_session.query(User).all()
    print(f"Remaining users after clear: {remaining}", file=sys.stderr)
    print("2", file=sys.stderr)
    # Remove any hanging sessions
    db_session.remove()
    print("3", file=sys.stderr)
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

# Wrapper around test_client that adds convenient authentication methods
@pytest.fixture
def auth(client):
    return AuthActions(client)

# Basic sanity test
def test_postgresql_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1

# Product fixture for Transaction tests
@pytest.fixture
def sample_product(logged_in_user):
    product = Product(
        product_name="Test Product",
        category="Test Product Category",
        barcode="123456",
        net_weight=200,
        unit_type="g",
        calories_per_100g=150,
        user_id=logged_in_user.id
    )
    db_session.add(product)
    db_session.flush()
    return product