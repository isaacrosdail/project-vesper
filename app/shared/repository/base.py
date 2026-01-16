from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.orm import Session

from sqlalchemy import func, select

from app._infra.db_base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository for database operations on user-scoped models.

    Provides CRUD operations filtered by user_id. Subclass for specific models.
    """

    def __init__(self, session: Session, user_id: int, model_cls: type[T]) -> None:
        self.session = session
        self.user_id = user_id
        self.model_cls = model_cls

    def add(self, item: T) -> T:
        self.session.add(item)
        return item

    def delete(self, item: T) -> T:
        self.session.delete(item)
        return item

    def _user_select(self, model_cls: type[T]) -> Select[tuple[T]]:
        return select(model_cls).where(model_cls.user_id == self.user_id)

    def get_all(self) -> list[T]:
        stmt = select(self.model_cls).where(self.model_cls.user_id == self.user_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_count_all(self) -> int:
        """Returns count."""
        stmt = select(func.count(self.model_cls.id)).where(
            self.model_cls.user_id == self.user_id
        )
        return self.session.execute(stmt).scalar() or 0

    def get_by_id(self, item_id: int) -> T | None:
        stmt = select(self.model_cls).where(
            self.model_cls.user_id == self.user_id, self.model_cls.id == item_id
        )
        return self.session.execute(stmt).scalars().first()
