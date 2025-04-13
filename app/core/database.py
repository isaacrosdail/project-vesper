# Centralized DB setup file

from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.db_base import Base
import app.modules.groceries.models
import app.modules.tasks.models

_engine = None # Global connection cache

# Function to get engine from the config
def get_engine(config):

    # Debug print
    print(" get_engine() CALLED")
    
    global _engine
    if _engine is None:
        db_uri = config.get("SQLALCHEMY_DATABASE_URI")
        print(db_uri) # DEBUG PRINT
        _engine = create_engine(db_uri)
    return _engine

# Trying out scoped session and session manager pattern to reduce .close() headaches
db_session = scoped_session(sessionmaker())

def init_db(config):
    engine = get_engine(config)
    db_session.configure(bind=engine) # Binds Session globally
    Base.metadata.create_all(engine)

# Optional, can delete
def get_db_session():
    return db_session()