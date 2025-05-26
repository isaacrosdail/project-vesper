"""
DB infrastructure & schema tests
Structure, lifecycle, connection tests go here
"""
# Standard lib imports
import pytest
# Third-party lib imports
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# Local app imports
from app.core.database import get_engine
from app.modules.tasks.models import Task


def test_db_connection(app):
    engine = get_engine(app.config)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1

# Schema check
def test_tables_exist(app):
    engine = get_engine(app.config)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "tasks" in tables
    assert "product" in tables
    assert "transaction" in tables

# Ensures DB integrity is enforced
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