## DB infrastructure & schema tests
## Structure, lifecycle, connection tests go here

# region Imports
# Basic imports
import pytest
from sqlalchemy import inspect, text

from sqlalchemy.orm import sessionmaker
from app.core.database import get_engine

# Import Models
from app.modules.tasks.models import Task
from app.modules.groceries.models import Product

# Imports for exceptions
from sqlalchemy.exc import IntegrityError

# endregion

def test_db_connection(app):
    engine = get_engine(app.config)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1

def test_tables_exist(app):
    engine = get_engine(app.config)
    inspector = inspect(engine)
    assert "tasks" in inspector.get_table_names()

def test_insert_and_query_task(app):
    engine = get_engine(app.config)
    Session = sessionmaker(bind=engine)
    session = Session()

    task = Task(title="Test Task", type="todo")
    session.add(task)
    session.commit()

    result = session.query(Task).filter_by(title="Test Task").first()
    assert result.type == "todo"

    session.close()

def test_unique_constraint_violation(app):
    engine = get_engine(app.config)
    Session = sessionmaker(bind=engine)
    session = Session()

    task1 = Task(title="Dupe Task", type="todo")
    task2 = Task(title="Dupe Task", type="todo")

    session.add_all([task1, task2])

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
    session.close()

def test_rollback_behavior(app):
    engine = get_engine(app.config)
    Session = sessionmaker(bind=engine)
    session = Session()

    task = Task(title="rollback", type="todo")
    session.add(task)
    session.rollback()

    result = session.query(Task).filter_by(title="rollback").first()
    assert result is None
    session.close()