from __future__ import annotations

from datetime import date
from enum import StrEnum, auto

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app._infra.db_base import Base

PASSWORD_MIN_LENGTH = 5
PASSWORD_MAX_LENGTH = 128

NAME_MIN_LENGTH = 1

NAME_MAX_LENGTH = 50
NAME_REGEX = rf"^[\p{{L}}' -]{{0,{NAME_MAX_LENGTH}}}$"
NAME_CHARSET = (
    f"Name must be {NAME_MIN_LENGTH}-{NAME_MAX_LENGTH} characters "
    "and may only include letters, spaces, apostrophes, and hyphens"
)
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
# Username: 3-30, Unicode letters, numbers, & underscores
USERNAME_REGEX = rf"^[\p{{L}}0-9_]{{{USERNAME_MIN_LENGTH},{USERNAME_MAX_LENGTH}}}$"

# CONSTANTS
PASSWORD_HASH_MAX_LENGTH = 256
TIMEZONE_MAX_LENGTH = 50

class UserRoleEnum(StrEnum):
    OWNER = auto()
    ADMIN = auto()
    USER = auto()
    DEMO = auto()

class UnitSystemEnum(StrEnum):
    METRIC = auto()
    IMPERIAL = auto()


class User(Base, UserMixin):  # type: ignore[misc]
    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH), nullable=False, unique=True
    )

    name: Mapped[str | None] = mapped_column(String(NAME_MAX_LENGTH), nullable=True)

    # Werkzeug's default uses pbkdf2:sha256 = ~95 chars
    password_hash: Mapped[str] = mapped_column(
        String(PASSWORD_HASH_MAX_LENGTH), nullable=False
    )

    role: Mapped[UserRoleEnum] = mapped_column(
        SAEnum(UserRoleEnum, name="user_role_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRoleEnum.USER,
        server_default="user"
    )

    # valid IANA tz_str
    timezone: Mapped[str] = mapped_column(
        String(TIMEZONE_MAX_LENGTH), nullable=False
    )

    profile: Mapped[UserProfile] = relationship("UserProfile", back_populates="user", lazy="joined", cascade="all, delete-orphan")
    goals: Mapped[UserGoals] = relationship("UserGoals", back_populates="user", lazy="joined", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} username: {self.username} role={self.role}>"

    def hash_password(self, plaintext: str) -> None:
        """Hash + salt + store."""
        self.password_hash = generate_password_hash(plaintext, salt_length=16)

    def check_password(self, provided_password: str) -> bool:
        if self.password_hash == self.UNUSABLE_PASSWORD:
            return False
        return check_password_hash(self.password_hash, provided_password)

    UNUSABLE_PASSWORD = "!"

    def set_unusable_password(self) -> None:
        self.password_hash = self.UNUSABLE_PASSWORD

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


# Unicode CLDR hour cycle
# Makes it easy with JS's Intl hourCycle opt
class HourCycleEnum(StrEnum):
    H12 = auto()
    H23 = auto() # midnight is 00:00, EOD at 23:59

class SexEnum(StrEnum):
    M = auto()
    F = auto()

class UserProfile(Base):

    __table_args__ = (
        CheckConstraint(
            "birth_date > '1900-12-31' AND birth_date < CURRENT_DATE",
            name="birth_date_range"
        ),
        CheckConstraint(
            "num_nonnulls(city, country, latitude, longitude) IN (0, 4)",
            name="location_all_or_none",
        ),
    )

    # Override Base's
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    unit_system: Mapped[UnitSystemEnum] = mapped_column(
        SAEnum(
            UnitSystemEnum,
            name="unit_system_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )

    hour_cycle: Mapped[HourCycleEnum] = mapped_column(
        SAEnum(
            HourCycleEnum,
            name="hour_cycle_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )

    # At save, ping OpenWeatherAPI's Geocodign API if city,country resolves.
    #   if yes, store what it returns, if not, reject input.
    city: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # country: ISO 3166-1 alpha-2
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # For WeatherAPI pings; derived from geocode
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    sex: Mapped[SexEnum | None] = mapped_column(
        SAEnum(
            SexEnum, name="sex_enum", values_callable=lambda x: [e.value for e in x]
        ),
        nullable=True
    )

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="profile")


CAL_PER_GRAM = {"protein": 4, "carbs": 4, "fat": 9}

class UserGoals(Base):
    __tablename__ = "user_goals"

    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(protein_pct, carbs_pct, fat_pct) = 0 "
            "OR (num_nonnulls(protein_pct, carbs_pct, fat_pct) = 3 AND protein_pct + carbs_pct + fat_pct = 100)",
            name="macro_split_complete",
        ),
        CheckConstraint("protein_pct BETWEEN 0 AND 100", name="protein_pct_range"),
        CheckConstraint("carbs_pct   BETWEEN 0 AND 100", name="carbs_pct_range"),
        CheckConstraint("fat_pct     BETWEEN 0 AND 100", name="fat_pct_range"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    weight: Mapped[float | None] = mapped_column(Float, nullable=True)      # kg, always - same canonical-unit rule as metrics
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protein_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fat_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carbs_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    potassium: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sodium: Mapped[int | None] = mapped_column(Integer, nullable=True)

    @property
    def protein(self) -> int | None:
        if self.calories is None or self.protein_pct is None:
            return None
        return round(self.calories * self.protein_pct / 100 / CAL_PER_GRAM["protein"])

    @property
    def carbs(self) -> int | None:
        if self.calories is None or self.carbs_pct is None:
            return None
        return round(self.calories * self.carbs_pct / 100 / CAL_PER_GRAM["carbs"])

    @property
    def fat(self) -> int | None:
        if self.calories is None or self.fat_pct is None:
            return None
        return round(self.calories * self.fat_pct / 100 / CAL_PER_GRAM["fat"])

    user: Mapped[User] = relationship("User", back_populates="goals")

