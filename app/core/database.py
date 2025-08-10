# Centralized DB setup file
# TODO: Rectify & expand notes on this to study

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Below we're using a connection pool singleton
# Only creating one engine across entire app
# All sessions & metadata bind to the same underlying connection
# If we drop+create tables on this engine, and don't clear the scoped session, then:
# Our app is using a session object tied to an old, now-invalid schema.
_engine = None # Global connection cache

# Function to get engine from the config
# 1. get_engine()     -> creates/returns singleton engine
# 2. init_db()        -> binds db_session to that engine
# 3. db_session() -> creates sessions using that engine
def get_engine(config):
    
    global _engine

    if _engine is None:
        db_uri = config.get("SQLALCHEMY_DATABASE_URI")
        _engine = create_engine(db_uri)
    return _engine

# Trying out scoped session and session manager pattern to reduce .close() headaches
# This is Flask's common pattern
# - You get a new session for each request context
# - But it's thread-local, so unless we call remove(), it persists even after table drops
# db_session is a registry (a factory that creates sessions)
db_session = scoped_session(sessionmaker())

def init_db(config):
    """
    Initialize the database session binding.

    Creates an SQLAlchemy engine from the given config, binds it to the global session (db_session), and configures it for app use.
    Skipping table creation, as Alembic handles schema changes.
    """
    engine = get_engine(config)         # Creates DB connection TODO: NOTES: Expand/improve this
    db_session.configure(bind=engine)   # Binds session globally => Tells SQLAlchemy: "Use this engine for all sessions"


# Making our own context manager
@contextmanager
def database_connection():
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise # re-raises errors?
    finally:
        session.close()