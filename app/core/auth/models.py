from app.core.db_base import Base
from sqlalchemy import Column, String


class User(Base):

    username = Column(String(50), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    # TODO: add password_hash (& salting)