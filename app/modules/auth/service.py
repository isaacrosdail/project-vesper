from __future__ import annotations

import os
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from flask.typing import ResponseReturnValue

    from app._infra.db_base import Base
    from app.modules.auth.repository import UsersRepository

from flask import abort, current_app, request
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.modules.auth.models import User, UserLangEnum, UserRoleEnum
from app.shared.database.seed.seed_db import seed_data_for

P = ParamSpec("P")
R = TypeVar("R")

EXEMPT_METHODS = {"OPTIONS"}  # copied from Flask-Login's source


def owner_required(
    func: Callable[P, ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]:
    """
    Decorator that ensures current_user is authenticaed and has OWNER role.

    Returns 403 Forbidden if user lacks owner permissions.
    """

    @wraps(func)
    @typed_login_required
    def decorated_view(*args: P.args, **kwargs: P.kwargs) -> ResponseReturnValue:
        if not current_user.is_owner:
            return abort(403, description="Owner privileges required")
        return func(*args, **kwargs)

    return decorated_view


def typed_login_required(
    func: Callable[P, ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]:
    """
    Typed version of Flask-Login's `login_required`.
    """

    @wraps(func)
    def decorated_view(*args: P.args, **kwargs: P.kwargs) -> ResponseReturnValue:
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()  # type: ignore[no-any-return, attr-defined]

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)  # type: ignore[no-any-return]
        return func(*args, **kwargs)

    return decorated_view


def check_item_ownership[T: Base](item: T, user_id: int) -> None:
    """Ensure item belongs to given user. Triggers abort(403) if not."""
    if hasattr(item, "user_id") and item.user_id != user_id:
        abort(404)


class AuthService:
    def __init__(self, repository: UsersRepository) -> None:
        self.repo = repository

    def register_user(
        self,
        *,
        username: str,
        password: str,
        name: str | None = None,
        role: UserRoleEnum = UserRoleEnum.USER,
        lang: UserLangEnum = UserLangEnum.EN,
    ) -> dict[str, Any]:
        """Create user account.
        Must be pre-validated. Sets defaults: userRole.USER, userLang.EN
        """

        try:
            user = self.repo.create_user(username, password, name, role, lang)
        except IntegrityError:
            return {"success": False, "message": "Username already exists"}
        else:
            return {"success": True, "user": user}

    def get_or_create_template_user(
        self, user_type: str, *, seed_data: bool = True
    ) -> type[User]:
        """Return an existing template user or create one.

        If the user doesn't exist, it's created from a template.
        When seed_data=True (default), initial related data is seeded via
        seed_data_for() immediately after creation.
        """
        user_configs: dict[str, Any] = {
            "demo": {
                "username": "guest",
                "password": "demo123",
                "name": "Guest",
                "role": UserRoleEnum.USER,
                "lang": UserLangEnum.EN,
            },
            "owner": {
                "username": "owner",
                "password": os.environ.get("OWNER_PASSWORD"),
                "name": "Owner",
                "role": UserRoleEnum.OWNER,
                "lang": UserLangEnum.EN,
            },
        }
        config = user_configs[user_type]
        if user_type == "owner" and not config.get("password"):
            msg = "Missing OWNER_PASSWORD env var for owner template user"
            raise RuntimeError(msg)
        user = self.repo.get_user_by_username(config["username"])

        if not user:
            user = self.repo.create_user(**config)
            if seed_data:
                seed_data_for(self.repo.session, user)
        return user
