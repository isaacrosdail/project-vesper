
from sqlalchemy import select, func

class BaseRepository:
    """Constructor for base class."""
    def __init__(self, session, user_id: int, user_tz: str = "UTC", model_cls = None):
        self.session = session
        self.user_id = user_id
        self.user_tz = user_tz
        self.model_cls = model_cls


    def add(self, item):
        self.session.add(item)
        return item
    
    def delete(self, item):
        self.session.delete(item)
        return item

    # Returns -> Select[Tuple[model_cls]] statement
    def _user_select(self, model_cls):
        return select(model_cls).where(
            model_cls.user_id == self.user_id
        )
    # Returns -> list[self.model_cls]
    def get_all(self):
        stmt = select(self.model_cls).where(
            self.model_cls.user_id == self.user_id
        )
        return self.session.execute(stmt).scalars().all()

    # .scalar() returns count OR None if 0, so we'll return 0 in that case
    def get_count_all(self) -> int:
        stmt = select(func.count(self.model_cls.id)).where(
            self.model_cls.user_id == self.user_id
        )
        return self.session.execute(stmt).scalar() or 0


    def get_by_id(self, item_id):
        stmt = select(self.model_cls).where(
            self.model_cls.user_id == self.user_id,
            self.model_cls.id == item_id
        )
        return self.session.execute(stmt).scalars().first()