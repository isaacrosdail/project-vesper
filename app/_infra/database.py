"""
Centralized SQLAlchemy DB setup.

Uses one global engine + scoped sessions for consistent, thread-safe DB access.

Note to self: First two imports are for 1) making custom context manager and 2) making it a decorator
"""
from contextlib import contextmanager
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Global _engine (singleton across app)
_engine = None # Global connection cache

# Ensures all sessions/metadata bind to the same underlying connection
def get_engine(config):
    """
    Return global SQLAlchemy engine (singleton).
    Creates on first call, reuses afterward.
    Note: pool_pre_ping handles stale connections.
    """
    global _engine
    if _engine is None:
        db_uri = config.get("SQLALCHEMY_DATABASE_URI")
        _engine = create_engine(db_uri, pool_pre_ping=True)
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
        # Close the *current* Session, scoped registry keeps per-thread identity?
        session.close()

# Making our own decorator out of our own context manager
# 'f' is a reference to our original function
# Decorator creates a wrapper that calls our original function
# with extra stuff (the session)
def with_db_session(f):
    """
    Decorator that injects a database session as the first parameter.
    
    The decorated function must accept 'session' as its first parameter.
    Automatically handles session commit/rollback/close via context manager.
    
    Usage:
        @with_db_session
        def my_function(session, other_params):
            # Use session here
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with database_connection() as session:
            return f(session, *args, **kwargs)
    return decorated_function