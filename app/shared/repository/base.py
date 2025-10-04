

class BaseRepository:
    """Constructor for base class."""
    def __init__(self, session, user_id: int, user_tz: str = "UTC", model_cls = None):
        self.session = session
        self.user_id = user_id
        self.user_tz = user_tz
        self.model_cls = model_cls

    def get_all(self):
        return self.session.query(self.model_cls).filter(
            self.model_cls.user_id == self.user_id
        ).all()
    
    def get_by_id(self, item_id):
        return self.session.query(self.model_cls).filter(
            self.model_cls.user_id == self.user_id,
            self.model_cls.id == item_id
        ).first()
    
    def add(self, item):
        self.session.add(item)
        return item
    
    def delete(self, item):
        self.session.delete(item)
        return item
    
    # Leaving the end blank (no .first()/.all(), etc) lets caller decide what to use there
    def _user_query(self, model_cls):
        return self.session.query(model_cls).filter(
            model_cls.user_id == self.user_id,
        )