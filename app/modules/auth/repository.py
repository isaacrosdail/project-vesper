"""
AuthRepository class doesn't make sense here yet, but will add for some useful "post-auth" operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from sqlalchemy import select

from app.modules.auth.models import User, UserLangEnum, UserPreference, UserRoleEnum
from app.shared.repository.base import BaseRepository


class UsersRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_user(
        self,
        username: str,
        password: str,
        name: str | None,
        role: UserRoleEnum,
        lang: UserLangEnum,
    ) -> User:
        user = User(username=username, name=name, role=role, lang=lang)
        user.hash_password(password)
        self.session.add(user)
        return user

    def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_user_by_user_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()


class UserPreferenceRepository(BaseRepository[UserPreference]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=UserPreference)
    # model = UserPreference

    def upsert(self, key: str, value: str) -> UserPreference:
        # find existing or create new TODO: Clean up/formalize
        stmt = (
            self._user_select(UserPreference).where(UserPreference.key == key)
        )
        existing = self.session.execute(stmt).scalars().first()
        if existing:
            existing.value = value
            return existing
        new_pref = UserPreference(user_id=self.user_id, key=key, value=value)
        self.session.add(new_pref)
        return new_pref

