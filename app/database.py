# Centralized DB setup file

from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db_base import Base
import app.modules.groceries.models
import app.modules.tasks.models

_engine = None # Global connection cache

# Function to get engine from the config
def get_engine(config):
    global _engine
    if _engine is None:
        db_uri = config.get("SQLALCHEMY_DATABASE_URI")
        _engine = create_engine(db_uri)
    return _engine

# Function to get a session bound to the engine
def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

def get_db_session():
    # Get engine based on current app's configuration
    engine = get_engine(current_app.config)
    # Get & return the session bound to that engine
    return get_session(engine)

def init_db():
    engine = get_engine(current_app.config)
    print("Engine ID:", id(engine))
    Base.metadata.create_all(engine)