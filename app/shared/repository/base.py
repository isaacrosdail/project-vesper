

class BaseRepository:
    """Constructor for base class."""
    def __init__(self, session, user_id: int, user_tz: str = "UTC"):
        self.session = session
        self.user_id = user_id
        self.user_tz = user_tz