# Holds fixtures & test config, automatically loaded by pytest (import not req'd)

import pytest
from app import create_app
from app.core.database import get_engine
from app.core.db_base import Base
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import time
import subprocess
print("conftest loaded!")

############### Ensure Docker PostgreSQL container is running before tests start
@pytest.fixture(scope="session", autouse=True)
def ensure_docker_postgres():
    print("Ensuring vesper-db is running...")

    # Check if already running
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", "name=vesper-db"],
        capture_output=True, text=True
    )

    if not result.stdout.strip():
        print("Starting vesper-db container...")
        subprocess.run(["docker", "start", "vesper-db"])
        time.sleep(3) # Let it initialize

# Create app once and use it for all tests
@pytest.fixture(scope="session")
def app():
    print("Starting app function in conftest...")
    app = create_app("testing")  # Create with 'testing' config
    print("TEST DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    time.sleep(2)
    #with app.app_context():
        #engine = get_engine(app.config)
        #Base.metadata.create_all(engine)
        #yield app
    yield app

# Fixture to reset the database before each test (optional, for clean slate)
@pytest.fixture(scope="session", autouse=True)
def reset_db(app):
    engine = get_engine(app.config)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT") # Study this later!!

        print("Dropping schema...")
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))

        print("Recreating schema...")
        conn.execute(text("CREATE SCHEMA public;"))

    # Import DB stuff
    from app.modules.groceries import models as grocery_models
    from app.modules.tasks import models as tasks_models
    print("Creating tables...")
    Base.metadata.create_all(engine)

## TRY THIS OUT
@pytest.fixture(scope="session")
def engine(app):
    return get_engine(app.config)

# Fixture to provide SQLAlchemy session
@pytest.fixture
def db_session(engine):
    #def db_session(app):
    #engine = get_engine(app.config)
    Session = sessionmaker(bind=engine)
    session = Session()
    # added
    trans = session.begin_nested() # < nested = rollbackable data
    # Try/finally here ensures we only rollback AFTER a test completes
    try:
        yield session
    #session.rollback()
    finally:
        trans.rollback()
        session.close()

# Fake browser to test routes (lets us send requests from a fake browser/client)
@pytest.fixture
def client(app):
    return app.test_client()

# Basic sanity test
def test_postgresql_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1