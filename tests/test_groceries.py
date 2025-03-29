import pytest
from modules.groceries.models import Base, get_session, Product, Transaction, handle_barcode
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker ##??
from datetime import date

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:") ## Test DB in-memory
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    return Session()