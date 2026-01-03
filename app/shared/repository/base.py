from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Any, Type

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    
from app._infra.db_base import Base
from sqlalchemy import select, func

T = TypeVar('T', bound=Base)           # Generic type for the primary model itself
TModel = TypeVar('TModel', bound=Base) # Any model for add/delete

class BaseRepository(Generic[T]):
    """Constructor for base class."""
    def __init__(self, session: 'Session', user_id: int, model_cls: Type[T]) -> None:
        self.session = session
        self.user_id = user_id
        self.model_cls = model_cls


    def add(self, item: TModel) -> TModel:
        self.session.add(item)
        return item
    
    def delete(self, item: TModel) -> TModel:
        self.session.delete(item)
        return item

    # Returns -> Select[Tuple[model_cls]] statement
    def _user_select(self, model_cls: Type[TModel]) -> Any:
        return select(model_cls).where(
            model_cls.user_id == self.user_id
        )

    # Returns -> list[self.model_cls]
    def get_all(self) -> list[T]:
        stmt = select(self.model_cls).where(
            self.model_cls.user_id == self.user_id
        )
        return list(self.session.execute(stmt).scalars().all())

    # .scalar() returns count OR None if 0, so we'll return 0 in that case
    def get_count_all(self) -> int:
        stmt = select(func.count(self.model_cls.id)).where(
            self.model_cls.user_id == self.user_id
        )
        return self.session.execute(stmt).scalar() or 0

    def get_by_id(self, item_id: int) -> T | None:
        stmt = select(self.model_cls).where(
            self.model_cls.user_id == self.user_id,
            self.model_cls.id == item_id
        )
        return self.session.execute(stmt).scalars().first()