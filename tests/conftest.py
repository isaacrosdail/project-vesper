# Holds fixtures & test config, automatically loaded by pytest (import not req'd)

import pytest
from app import create_app
from app.database import get_engine, get_db_session, init_db
from app.db_base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Injected by pytest-postgresql
@pytest.fixture
def engine(postgresql_proc):
    return create_engine(postgresql_proc.dsn()) # Gives us a test DB per session

# Create app once and use it for all tests
@pytest.fixture
def app(engine):
    app = create_app("testing")  # Create with 'testing' config

    # Override or patch the DB connection if needed
    # This line ensures we point to testing db 
    app.config['SQLALCHEMY_DATABASE_URI'] = str(engine.url)

    with app.app_context():
        Base.metadata.create_all(engine)
        yield app

@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session
    yield session
    session.rollback()
    session.close()

# Gives us a fake browser to send requests from
@pytest.fixture
def client(app):
    return app.test_client()