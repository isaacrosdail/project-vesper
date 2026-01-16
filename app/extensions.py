"""
Flask extensions initialized here to avoid circular imports.
Import these in other modules instead of importing from app.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

    from app.modules.auth.models import User

from flask_caching import Cache
from flask_login import LoginManager

from app._infra.database import db_session
from app.modules.auth.models import User

# Create extension instances
cache = Cache()
login_manager = LoginManager()


def _setup_extensions(app: Flask) -> None:
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # <- where @login_required redirects

    @login_manager.user_loader  # type: ignore[misc]
    def load_user(user_id: int) -> User | None:
        """
        Callback required for Flask-Login.

        Called outside normal request flow, whenever Flask-Login needs to reload
        the User object, even between requests.
        """
        return db_session.get(User, int(user_id))

    # Init Flask-Caching
    app.config.from_mapping(
        {
            "CACHE_TYPE": "SimpleCache",
            "CACHE_DEFAULT_TIMEOUT": 300,
        }
    )
    cache.init_app(app)
