from werkzeug.security import generate_password_hash, check_password_hash
from app.core.db_base import Base
from sqlalchemy import Column, String
from flask_login import UserMixin

class User(Base, UserMixin):
    username = Column(String(50), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    password_hash = Column(String(256), nullable=False) # Large enough? bcrypt = 60chars, Werkzeug's default uses pbkdf2:sha256 = around 95 chars
    role = Column(String(50), nullable=False, default="user")

    # Instance methods
    def set_password(self, plaintext: str) -> None:
        """Hash + salt + store."""
        self.password_hash = generate_password_hash(
            plaintext,
            salt_length=16
        )
    
    def check_password(self, provided_password: str) -> bool:
        """Return True if provided_password matches stored hash."""
        return check_password_hash(self.password_hash, provided_password)