# Holds fixtures & test config, automatically loaded by pytest (import not req'd)

import pytest
import psycopg2
import subprocess
import time
from app import create_app
from app.database import get_engine, get_db_session, init_db
from app.db_base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

print("conftest loaded!")

# Fixture to start PostgreSQL container using Docker
@pytest.fixture(scope="session")
def postgres_connection():

    # Check if container is already running using 'docker ps'
    container_status = subprocess.run(
        ["docker", "ps", "-q", "-f", "name=vesper-db"],
        capture_output=True, text=True
    )

    # If container is not running, start it
    if not container_status.stdout:
        print("Starting PostgreSQL container...")
        subprocess.run([
            "docker", "start", "vesper-db"
        ])
        # Wait for it to initialize
        time.sleep(5)

    # Connect to the PostgreSQL container
    conn = psycopg2.connect(
        dbname="vesper_test", 
        user="vesper",
        password="vesperpass",
        host="localhost",
        port=5433
    )
    
    yield conn  # Provide the connection to tests
    
    print("PostgreSQL container is being reused")

# Fixture to reset the database before each test (optional, for clean slate)
@pytest.fixture(autouse=True)
def reset_db(postgres_connection):
    cursor = postgres_connection.cursor()
    cursor.execute("DROP SCHEMA public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")
    postgres_connection.commit()
    cursor.close()
    print("Database reset.")

# Create app once and use it for all tests
@pytest.fixture
def app(postgres_connection):
    print("Starting app function in conftest...")
    app = create_app("testing")  # Create with 'testing' config

    # Override or patch the DB connection if needed
    # This line ensures we point to testing db 
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://vesper:vesperpass@localhost:5432/vesper_test"

    with app.app_context():
        Base.metadata.create_all(postgres_connection)
        yield app

# Fixture to create a database session
@pytest.fixture
def db_session(postgres_connection):
    print("Starting db_session function in conftest...")
    Session = sessionmaker(bind=postgres_connection)
    session = Session
    yield session
    session.rollback()
    session.close()

# Gives us a fake browser to send requests from
@pytest.fixture
def client(app):

    return app.test_client()

# Example test to check PostgreSQL connection
def test_postgresql_connection(postgres_connection):
    print(f"PostgreSQL connection established: {postgres_connection}")
    cursor = postgres_connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result == (1,)