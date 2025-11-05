import enum

from flask_login import UserMixin
from sqlalchemy import Column, String
from sqlalchemy import Enum as SAEnum
from werkzeug.security import check_password_hash, generate_password_hash

from app._infra.db_base import Base
from app.modules.auth.constants import USERNAME_MAX_LENGTH, NAME_MAX_LENGTH, TIMEZONE_MAX_LENGTH

# CONSTANTS
PASSWORD_HASH_MAX_LENGTH = 256

class UserRoleEnum(enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    USER = "USER"

# Lower case (ISO codes)
class UserLangEnum(enum.Enum):
    EN = "en"
    DE = "de"

class UnitSystemEnum(enum.Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"

class User(Base, UserMixin):
    username = Column(
        String(USERNAME_MAX_LENGTH),
        nullable=False,
        unique=True
    )

    name = Column(
        String(NAME_MAX_LENGTH),
        nullable=True
    )
    
    # Werkzeug's default uses pbkdf2:sha256 = ~95 chars
    password_hash = Column(
        String(PASSWORD_HASH_MAX_LENGTH),
        nullable=False
    ) 

    role = Column(
        SAEnum(UserRoleEnum, name="user_role_enum"), 
        nullable=False,
        default=UserRoleEnum.USER
    )

    timezone = Column(
        String(TIMEZONE_MAX_LENGTH),
        nullable=False, 
        server_default="America/Chicago"
    )

    lang = Column(
        SAEnum(UserLangEnum, name="user_lang_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserLangEnum.EN
    )

    city = Column(String(100), nullable=False, server_default='Chicago')
    
    country = Column(String(3), nullable=False, server_default='US')

    units = Column(
        SAEnum(UnitSystemEnum,
               name="unit_system_enum",
               values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UnitSystemEnum.IMPERIAL,
        server_default='imperial'
    )

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
        return self.role == UserRoleEnum.OWNER
    
    @property
    def is_admin(self):
        return self.role == UserRoleEnum.ADMIN
    
    # Helpful instance method to check role
    # EX: if current_user.has_role(UserRole.OWNER)
    def has_role(self, role: UserRoleEnum) -> bool:
        return self.role == role