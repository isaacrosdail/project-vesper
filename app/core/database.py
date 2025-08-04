# Centralized DB setup file

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

    # Debug: print _engine's current state
    # print(f"_engine is None: {_engine is None}")

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
    engine = get_engine(config)         # Creates DB connection
    db_session.configure(bind=engine) # Binds Session globally -> Tells SQLAlchemy: "Use this engine for all sessions"
    # Base.metadata.create_all(engine)  # Removed: We now delete DATA not tables & let Alembic migrations handle the rest


# Making our own context manager
@contextmanager
def database_connection():
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()