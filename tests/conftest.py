# Holds fixtures & test config, automatically loaded by pytest (import not req'd)

import pytest
import psycopg2
import subprocess
import time
from app import create_app
from app.database import get_engine, get_db_session, init_db
from app.db_base import Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

print("conftest loaded!")

# Create app once and use it for all tests
@pytest.fixture
def app():
    print("Starting app function in conftest...")
    app = create_app("testing")  # Create with 'testing' config
    with app.app_context():
        engine = get_engine(app.config)
        Base.metadata.create_all(engine)
        yield app

# Fixture to reset the database before each test (optional, for clean slate)
@pytest.fixture(autouse=True)
def reset_db(app):
    engine = get_engine(app.config)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT") # Study this later!!
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        Base.metadata.create_all(engine)

# Fixture to provide SQLAlchemy session
@pytest.fixture
def db_session(app):
    engine = get_engine(app.config)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

# Fake browser to test routes (lets us send requests from a fake browser/client)
@pytest.fixture
def client(app):
    return app.test_client()

# Basic sanity test
def test_postgresql_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1