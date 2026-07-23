"""
AuthRepository class doesn't make sense here yet, but will add for some useful "post-auth" operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from sqlalchemy import func, select

from app.modules.auth.models import User, UserRoleEnum


class UsersRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_user_by_user_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def delete_stale_demo_users(self, cutoff: datetime) -> int:
        users = self.session.scalars(
            select(User).where(
                User.role == UserRoleEnum.DEMO,
                User.created_at < cutoff,
            )
        ).all()
        for u in users:
            self.session.delete(u)
        return len(users)
