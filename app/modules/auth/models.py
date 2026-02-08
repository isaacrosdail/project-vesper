import enum

from flask_login import UserMixin
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app._infra.db_base import Base
from app.modules.auth.validation_constants import (
    NAME_MAX_LENGTH,
    TIMEZONE_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)

# CONSTANTS
PASSWORD_HASH_MAX_LENGTH = 256


class UserRoleEnum(enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    USER = "USER"


class UserLangEnum(enum.Enum):
    """Lower case (ISO)"""

    EN = "en"
    DE = "de"


class UnitSystemEnum(enum.Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"


class User(Base, UserMixin):  # type: ignore[misc]
    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH), nullable=False, unique=True
    )

    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=True)

    # Werkzeug's default uses pbkdf2:sha256 = ~95 chars
    password_hash: Mapped[str] = mapped_column(
        String(PASSWORD_HASH_MAX_LENGTH), nullable=False
    )

    role: Mapped[UserRoleEnum] = mapped_column(
        SAEnum(UserRoleEnum, name="user_role_enum"),
        nullable=False,
        default=UserRoleEnum.USER,
    )

    timezone: Mapped[str] = mapped_column(
        String(TIMEZONE_MAX_LENGTH), nullable=False, server_default="America/Chicago"
    )

    lang: Mapped[UserLangEnum] = mapped_column(
        SAEnum(
            UserLangEnum,
            name="user_lang_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=UserLangEnum.EN,
    )

    city: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="Chicago"
    )

    country: Mapped[str] = mapped_column(String(3), nullable=False, server_default="US")

    units: Mapped[UnitSystemEnum] = mapped_column(
        SAEnum(
            UnitSystemEnum,
            name="unit_system_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=UnitSystemEnum.IMPERIAL,
        server_default="imperial",
    )

    habits = relationship("Habit", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    daily_metrics = relationship("DailyMetrics", back_populates="user")
    products = relationship("Product", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    shopping_list = relationship("ShoppingList", back_populates="user")
    shopping_list_item = relationship("ShoppingListItem", back_populates="user")
    recipes = relationship("Recipe", back_populates="user")
    time_entry = relationship("TimeEntry", back_populates="user")
    habit_completion = relationship("HabitCompletion", back_populates="user")
    leet_code_record = relationship("LeetCodeRecord", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} username: {self.username} role={self.role}>"

    def hash_password(self, plaintext: str) -> None:
        """Hash + salt + store."""
        self.password_hash = generate_password_hash(plaintext, salt_length=16)

    def check_password(self, provided_password: str) -> bool:
        """Returns True if provided_password matches stored hash."""
        return check_password_hash(self.password_hash, provided_password)

    @property
    def is_owner(self) -> bool:
        """Returns `True` if user has role of `OWNER`."""
        return self.has_role(UserRoleEnum.OWNER)

    @property
    def is_admin(self) -> bool:
        """Returns `True` if user has role of `ADMIN`."""
        return self.has_role(UserRoleEnum.ADMIN)

    def has_role(self, role: UserRoleEnum) -> bool:
        """Returns `True` if user is of the given role."""
        return self.role == role
