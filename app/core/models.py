# Currently used to define our User model

from sqlalchemy import Column, String
from app.core.db_base import Base

class User(Base):

    username = Column(String(50), nullable=False, unique=True)
    # add password_hash later