import pytest
from sqlalchemy import inspect, text

from sqlalchemy.orm import sessionmaker
from app.core.database import get_engine

# Import Models
from app.modules.tasks.models import Task

# Imports for exceptions
from sqlalchemy.exc import IntegrityError

def test_insert_and_query_task(app):
    engine = get_engine(app.config)
    Session = sessionmaker(bind=engine)
    session = Session()

    task = Task(title="Test Task", type="todo")
    session.add(task)
    session.flush() # instead of commit

    result = session.query(Task).filter_by(title="Test Task").first()
    assert result.type == "todo"

    session.close()