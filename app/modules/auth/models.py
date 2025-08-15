from enum import Enum

from flask_login import UserMixin
from sqlalchemy import Column, String
from werkzeug.security import check_password_hash, generate_password_hash

from app._infra.db_base import Base


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"

class UserLang(str, Enum):
    EN = "en"
    DE = "de"

"""
SQLAlchemy's metaclass intercepts class creation, finds the Column objects we defined,
then _injects_ query methods like .query(), .filter(), etc.
It's why we can do User.query(..) despite never having defined a query attribute
"""
class User(Base, UserMixin):
    username = Column(String(50), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    password_hash = Column(String(256), nullable=False) # Large enough? bcrypt = 60chars, Werkzeug's default uses pbkdf2:sha256 = around 95 chars
    role = Column(String(20), nullable=False, default=UserRole.USER.value)
    timezone = Column(String(50), nullable=False, server_default="America/Chicago")
    lang = Column(String(20), nullable=False, server_default="en")

    def __repr__(self):
        return f"<User id={self.id} username: {self.username} role={self.role}>"

    # Instance methods
    def hash_password(self, plaintext: str) -> None:
        """Hash + salt + store."""
        self.password_hash = generate_password_hash(
            plaintext,
            salt_length=16
        )
    
    def check_password(self, provided_password: str) -> bool:
        """Return True if provided_password matches stored hash."""
        return check_password_hash(self.password_hash, provided_password)
    
    @property
    def is_owner(self):
        return self.role == UserRole.OWNER.value
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN.value
    
    # Helpful instance method to check role
    # EX: if current_user.has_role(UserRole.OWNER)
    def has_role(self, role: UserRole) -> bool:
        return self.role == role.value