# Centralized DB setup file
import os
from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.db_base import Base
import app.modules.groceries.models
import app.modules.tasks.models

# Below we're using a connection pool singleton
# Only creating one engine across entire app
# All sessions & metadata bind to the same underlying connection
# If we drop+create tables on this engine, and don't clear the scoped session, then:
# Our app is using a session object tied to an old, now-invalid schema.
_engine = None # Global connection cache

# Function to get engine from the config
# 1. get_engine()     -> creates/returns singleton engine
# 2. init_db()        -> binds db_session to that engine
# 3. get_db_session() -> creates sessions using that engine
def get_engine(config):

    # Debug print
    print(" get_engine() CALLED")
    
    global _engine

    # Get & print FLASK_ENV for debugging
    flask_env = os.environ.get('FLASK_ENV')
    print(f"Current FLASK_ENV: {flask_env}\n\n\n\n\n")

    # Check whats in the config
    db_uri = config.get("SQLALCHEMY_DATABASE_URI")
    print(f"Current DB URI from config: {db_uri}")

    # Print _engine's current state
    print(f"_engine is None: {_engine is None}")

    if _engine is None:
        db_uri = config.get("SQLALCHEMY_DATABASE_URI")
        print(db_uri) # DEBUG PRINT
        _engine = create_engine(db_uri)
    return _engine

# Trying out scoped session and session manager pattern to reduce .close() headaches
# This is Flask's common pattern
# - You get a new session for each request context
# - But it's thread-local, so unless we call remove(), it persists even after table drops
# db_session is a registry (a factory that creates sessions)
db_session = scoped_session(sessionmaker())

def init_db(config):
    engine = get_engine(config)
    db_session.configure(bind=engine) # Binds Session globally -> "Use this engine for all sessions"
    Base.metadata.create_all(engine)

# Optional, can delete
def get_db_session():
    return db_session()