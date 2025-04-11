# Holds fixtures & test config, automatically loaded by pytest (import not req'd)

import pytest
from app import create_app
from app.database import get_engine, get_db_session, init_db
from app.base import Base

# Create app once and use it for all tests
@pytest.fixture
def app():
    app = create_app("testing")  # Create app with 'testing' config
    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def db_session(app):
    with app.app_context():
        engine = get_engine(app.config)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        session = get_db_session()
        yield session
        session.rollback()
        session.close()

# Gives us a fake browser to send requests from
@pytest.fixture
def client(app):
    return app.test_client()