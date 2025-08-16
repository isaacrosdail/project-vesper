"""
Centralized SQLAlchemy DB setup.

Uses one global engine + scoped sessions for consistent, thread-safe DB access.
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Global _engine (singleton across app)
_engine = None # Global connection cache

# Ensures all sessions/metadata bind to the same underlying connection
def get_engine(config):
    """
    Return global SQLAlchemy engine (singleton).
    Creates on first call, reuses afterward.
    """
    global _engine
    if _engine is None:
        db_uri = config.get("SQLALCHEMY_DATABASE_URI")
        _engine = create_engine(db_uri)
    return _engine

# db_session: session registry/factory (creates one Session per thread/request)
# textbook: thread-local; new session per request, call remove() on schema change (stale sessions)
db_session = scoped_session(sessionmaker())

def init_db(config):
    """
    Bind global session (db_session) to the app engine.
    Schema creation handled externally (Alembic).

    Textbook: creates an SQLAlchemy engine from config, 
    binds it to db_session ("use this session for all sessions"), configures ORM for use.
    """
    engine = get_engine(config)
    db_session.configure(bind=engine)


# Making our own context manager
@contextmanager
def database_connection():
    """
    Provides a short-lived SQLAlchemy session with auto commit/rollback/close.

    Notes
    -----
    - Yields a new Session from db_session (thread-local factory).
    - On success => commits changes.
    - On error   => rolls back, re-raises.
    - *Always* closes session (releases connection).

    Example
    ------
        with database_connection() as session:
            session.add(obj)
            result = session.query(Model).all()
        
    ### Session is safely committed or rolled back, then closed.
    """
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()