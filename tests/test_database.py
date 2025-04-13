import pytest
from sqlalchemy import inspect
from app.database import get_engine, get_db_session, init_db
from app import create_app
from app.modules.tasks.models import Task
from app.modules.groceries.models import Product
from app.db_base import Base

def test_engine_creation(app):
    # Ensure engine is correctly created for testing config
    engine = get_engine(app.config)
    assert "5432" in str(engine.url)

def test_db_session(app):
    # Ensure session is correctly tied to the engine
    session = get_db_session()
    assert session is not None # Session should be created successfully
    assert "5432" in str(session.bind.url)

def test_init_db(app):
    # Ensure db tables are created after calling init_db()
    with app.app_context():
        init_db(app.config) # Initialize db (create tables)
        # Verify if the tasks table exists
        engine = get_engine(app.config)

        # SANITY CHECK
        print("Engine ID:", id(engine))

        print("Expected DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])
        print("Engine:", engine)

        print("Base.metadata.tables:", list(Base.metadata.tables.keys()))

        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Inspector sees tables:", tables)

        assert "tasks" in tables