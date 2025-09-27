"""
Houses fixtures & test config, automatically loaded by pytest.
"""

import pytest
from flask_login import login_user
from sqlalchemy import text

from app import create_app
from app._infra.database import db_session
from app.modules.auth.models import User
from app.shared.database.helpers import delete_all_db_data


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


# Create app once & use it for all tests
@pytest.fixture(scope="session")
def app():
    app = create_app('testing')  # Pass in our TestConfig
    with app.app_context():
        yield app


# Fixture to give us a logged in user to test with
@pytest.fixture
def logged_in_user(app): # add clear_tables as dependency to ensure it runs before this?
    """Creates a logged-in user for testing authenticated routes."""
    # Creates fake HTTP request context for testing
    # Makes Flask think it's handling a real web request
    # Enables things like request, session, current_user
    with app.test_request_context():
        user = User(
            username="Test_username", 
            name="Test_user", 
            role='USER'
        )
        user.hash_password('password123')
        db_session.add(user)
        db_session.flush()

        login_user(user)
        
    return user

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

# monkeypatches db_session() to use our test session
@pytest.fixture(autouse=True)
def patch_db_session(monkeypatch):
    from app._infra.database import \
        db_session as \
        global_session  # Imports scoped session factory and renames it to global_session

    # lambda *_: global_session() creates a function that takes any arguments ("*_" = "ignore whatever args are passed")
    #       and returns global_session() which calls our scoped session
    # This makes all imports of db_session use our test database
    monkeypatch.setattr("app._infra.database.db_session", lambda *_: global_session())

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

