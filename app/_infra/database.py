"""Centralized SQLAlchemy DB setup.

Uses one global engine + scoped sessions for consistent, thread-safe DB access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Concatenate, ParamSpec, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from sqlalchemy.engine import Engine

import logging
import sys
from contextlib import contextmanager
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, scoped_session, sessionmaker

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)

# Global _engine (singleton across app)
_engine = None  # Global connection cache


# Ensures all sessions/metadata bind to the same underlying connection
def get_engine(config: dict[str, Any]) -> Engine:
    """Return global SQLAlchemy engine (singleton).
    Creates on first call, reuses afterward.
    Note: pool_pre_ping handles stale connections.
    """
    global _engine  # noqa: PLW0603
    if _engine is None:
        db_uri = config.get("SQLALCHEMY_DATABASE_URI")
        if db_uri is None:
            msg = "SQLALCHEMY_DATABASE_URI not configured"
            raise ValueError(msg)

        _engine = create_engine(db_uri, pool_pre_ping=True)
    return _engine


# db_session: session registry/factory (creates one Session per thread/request)
# thread-local; new session per request, call remove() on schema change (stale sessions)
db_session = scoped_session(sessionmaker())


def init_db(config: dict[str, Any]) -> None:
    """Initialize database connection and configures global session.

    Creates SQLAlchemy engine from config, verifies that database is accessible, and
    binds it to the global `db_session` for use throughout the application.

    Schema creation and migrations handled externally (Alembic).

    Args:
        config: Database configuration dict

    Raises:
        SystemExit: If database connection fails (likely Postgres not running)
    """
    engine = get_engine(config)
    try:
        with engine.connect():
            pass
    except OperationalError:
        logger.debug(
            "\nDatabase is not running. Did you start the Postgres instance?\n"
        )
        sys.exit("Database is not running. Did you start the Postgres instance?")
    db_session.configure(bind=engine)


@contextmanager
def database_connection() -> Generator[Session, None, None]:
    """Provides a short-lived SQLAlchemy session with auto commit/rollback/close.

    Notes:
    -----
    - Yields a new Session from db_session (thread-local factory).
    - On success => commits changes.
    - On error   => rolls back, re-raises.
    - *Always* closes session (releases connection).

    Example:
    -------
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


def with_db_session(f: Callable[Concatenate[Session, P], R]) -> Callable[P, R]:
    """Decorator that injects a database session as the first parameter.

    The decorated function must accept 'session' as its first parameter.
    Automatically handles session commit/rollback/close via context manager.

    Usage:
        @with_db_session
        def my_function(session, other_params):
            # Use session here
    """

    @wraps(f)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R:
        with database_connection() as session:
            return f(session, *args, **kwargs)

    return decorated_function
