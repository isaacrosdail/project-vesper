# Holds fixtures and test config, automatically loaded by pytest (no need to import manually)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.groceries.models import Base

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(in_memory_db):
    Session = sessionmaker(bind=in_memory_db)
    session = Session()
    yield session
    session.close()