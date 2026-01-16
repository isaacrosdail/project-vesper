from __future__ import annotations

from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

from functools import wraps
import os

from flask import abort, current_app
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app.modules.auth.models import User, UserLangEnum, UserRoleEnum
from app.modules.auth.repository import UsersRepository
from app.shared.database.seed.seed_db import seed_data_for


def requires_owner(f: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator that ensures current_user is authenticaed and has OWNER role.

    Returns 403 Forbidden if user lacks owner permissions.
    """
    @wraps(f)
    @login_required # type: ignore[misc]
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R:
        # Check if user has owner role
        if not current_user.is_owner:
            return abort(403)
        # If they do, call original fuction (ie, proceed)
        return f(*args, **kwargs)
    return decorated_function

def check_item_ownership(item: Any, user_id: int) -> None:
    """Ensure item belongs to given user. Triggers abort(403) if not."""
    if hasattr(item, "user_id") and item.user_id != user_id:
        abort(403)


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


    def get_or_create_template_user(self, user_type: str, seed_data: bool = True) -> Any:
        """Find existing user template or create one, then seed data accordingly."""
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
