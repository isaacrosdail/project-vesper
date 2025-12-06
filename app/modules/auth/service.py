
from typing import Any, Callable

from functools import wraps

from flask import abort
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app.modules.auth.models import User, UserLangEnum, UserRoleEnum
from app.modules.auth.repository import UsersRepository
from app.shared.database.seed.seed_db import seed_data_for


# TODO: Prune these
# Custom decorator for enforcing owner role permissions
def requires_owner(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that ensures current_user is authenticaed and has OWNER role.

    Returns 403 Forbidden if user lacks owner permissions.
    """
    @wraps(f)
    @login_required # type: ignore[misc]
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        # Check if user has owner role
        if not current_user.is_owner:
            return abort(403)
        # If they do, call original fuction (ie, proceed)
        return f(*args, **kwargs)
    return decorated_function

def requires_role(role: UserRoleEnum) -> Callable[..., Any]:
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if not current_user.has_role(role):
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_item_ownership(item: Any, user_id: int) -> None:
    """Ensure item belongs to given user. Triggers abort(403) if not."""
    if hasattr(item, 'user_id') and item.user_id != user_id:
        abort(403)


class AuthService:
    def __init__(self, repository: UsersRepository):
        self.repo = repository

    def register_user(self, *, username: str, password: str, name: str | None = None,
                      role: UserRoleEnum = UserRoleEnum.USER,
                      lang: UserLangEnum = UserLangEnum.EN) -> dict[str, Any]:
        """Create user account. Must be pre-validated."""

        try:
            user = self.repo.create_user(username, password, name, role, lang)
            return {"success": True, "user": user}
        except IntegrityError:
            return {"success": False, "message": "Username already exists"}


    def get_or_create_template_user(self, user_type: str, seed_data: bool = True) -> Any:
        """Find existing user template or create one, then seed data accordingly."""
        user_configs: dict[str, Any] = {
            "demo": {
                "username": "guest",
                "password": "demo123",
                "name": "Guest",
                "role": UserRoleEnum.USER,
                "lang": UserLangEnum.EN
            },
            "owner": {
                "username": "owner",
                "password": "owner123",
                "name": "Owner",
                "role": UserRoleEnum.OWNER,
                "lang": UserLangEnum.EN
            }
        }
        config = user_configs[user_type]
        user = self.repo.get_user_by_username(config["username"])

        if not user:
            user = self.repo.create_user(**config)
            if seed_data:
                seed_data_for(self.repo.session, user)
        return user