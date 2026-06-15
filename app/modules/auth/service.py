from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any
from zoneinfo import available_timezones

if TYPE_CHECKING:

    from sqlalchemy.orm import Session

    from app.modules.auth.repository import UsersRepository

from sqlalchemy.exc import IntegrityError

from app.modules.auth.models import UnitSystemEnum, User, UserLangEnum, UserRoleEnum
from app.modules.auth.repository import UserPreferenceRepository, UsersRepository
from app.shared.database.seed.seed_db import seed_data_for
from app.shared.exceptions import ServiceError
from app.shared.models import Pillar


class AuthService:
    def __init__(self, session: Session, user_repo: UsersRepository, pref_repo: UserPreferenceRepository | None = None) -> None:
        self.session = session
        self.user_repo = user_repo
        self.pref_repo = pref_repo

    def register_user(
        self,
        *,
        username: str,
        password: str,
        name: str | None = None,
        role: UserRoleEnum = UserRoleEnum.USER,
        lang: UserLangEnum = UserLangEnum.EN,
    ) -> User:
        """Create user account.
        Must be pre-validated. Sets defaults: userRole.USER, userLang.EN
        """

        try:
            user: User = self.user_repo.create_user(username, password, name, role, lang)
            self.user_repo.session.flush()
            # Seed every user with core Pillars
            pillars = [
                Pillar(name="Health", user_id=user.id),
                Pillar(name="Career", user_id=user.id),
                Pillar(name="Purpose", user_id=user.id),
                Pillar(name="Rest", user_id=user.id),
                Pillar(name="Relationships", user_id=user.id),
            ]
            self.user_repo.session.add_all(pillars)
        except IntegrityError:
            # TODO: note, when we raise inside an except, Python attaches the original exception as
            # __cause__ or __context__.
            # from e = "this error was caused by that one" (shows both in tracebacks)
            # from None = "im intentionally replacing it, dont show the original"
            # TODO: This hits Postgres and therefore is "out of our hands" by this point, no?
            raise ServiceError("Username already exists") from None
        return user

    def get_or_create_template_user(
        self, user_type: str, *, seed_data: bool = True
    ) -> User:
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
        user = self.user_repo.get_user_by_username(config["username"])

        if not user:
            user = self.register_user(**config)
            if seed_data:
                seed_data_for(self.user_repo.session, user)
        return user


    # TODO: Fix this up
    def update_profile(self, user: User, data: dict[str, str]) -> User:
        if not self.pref_repo:
            raise ServiceError("no")

        WHITELIST = ["timezone", "units", "city", "country"]

        for field, val in data.items():
            if field not in WHITELIST:
                continue
            # validate enum fields
            if field == "units" and val not in [e.value for e in UnitSystemEnum]:
                raise ServiceError(f"Invalid unit system: {val}")
            if field == "timezone" and val not in available_timezones():
                raise ServiceError(f"Invalid timezone: {val}")
            setattr(user, field, val)
        return user


def create_auth_service(session: Session, user_id: int) -> AuthService:
    return AuthService(
        session=session,
        user_repo=UsersRepository(session),
        pref_repo=UserPreferenceRepository(session, user_id),
    )
