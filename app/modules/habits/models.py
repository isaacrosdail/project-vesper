"""
Model definitions for Habits module.
"""

import enum
from datetime import datetime
from typing import Any, ClassVar, Self

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.modules.habits.validation_constants import (
    HABIT_NAME_MAX_LENGTH,
    LC_TITLE_MAX_LENGTH,
    PROMOTION_THRESHOLD_MAX,
    PROMOTION_THRESHOLD_MIN,
)
from app.shared.datetime.helpers import convert_to_timezone
from app.shared.models import habit_tags
from app.shared.serialization import APISerializable
from app.shared.type_defs import OrderedEnum


class StatusEnum(OrderedEnum):
    EXPERIMENTAL = "EXPERIMENTAL"
    ESTABLISHED = "ESTABLISHED"


StatusEnum.sort_order = ["ESTABLISHED", "EXPERIMENTAL"]  # type: ignore[attr-defined]


class LCStatusEnum(OrderedEnum):
    SOLVED = "SOLVED"
    ATTEMPTED = "ATTEMPTED"
    REVIEWED = "REVIEWED"


LCStatusEnum.sort_order = ["SOLVED", "ATTEMPTED", "REVIEWED"]  # type: ignore[attr-defined]


class DifficultyEnum(OrderedEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


DifficultyEnum.sort_order = ["HARD", "MEDIUM", "EASY"]  # type: ignore[attr-defined]


class LanguageEnum(enum.Enum):
    PYTHON = "PYTHON"
    JS = "JS"
    CPP = "CPP"
    C = "C"

    def __lt__(self, other: Self) -> bool:
        return str(self.value) < str(other.value)


class Habit(Base, APISerializable):
    __api_exclude__: ClassVar[list[str]] = []

    # Use super() to "append to" our serializer's result dict to add derived keys
    def to_api_dict(self) -> dict[str, Any]:
        result = super().to_api_dict()
        result["is_promotable"] = (
            self.status is not None and self.promotion_threshold is not None
        )
        return result

    __table_args__ = (
        CheckConstraint(
            f"promotion_threshold is NULL OR (promotion_threshold >= {PROMOTION_THRESHOLD_MIN} AND promotion_threshold <= {PROMOTION_THRESHOLD_MAX})",
            name="ck_promotion_threshold_range_0_1",
        ),
        UniqueConstraint("user_id", "name", name="uq_user_habit_name"),
    )

    name: Mapped[str] = mapped_column(String(HABIT_NAME_MAX_LENGTH), nullable=False)

    status: Mapped[StatusEnum] = mapped_column(
        SAEnum(StatusEnum, name="status_enum"), nullable=True
    )

    established_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    promotion_threshold: Mapped[float] = mapped_column(Float, nullable=True)
    # Represents target completion rate per week
    target_frequency: Mapped[int] = mapped_column(Integer, nullable=False)

    @property
    def established_date_local(self) -> datetime | None:
        return convert_to_timezone(self.user.timezone, self.established_date)

    user = relationship("User", back_populates="habits")
    tags = relationship("Tag", secondary=habit_tags, back_populates="habits")
    habit_completions = relationship(
        "HabitCompletion", back_populates="habit", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Habit id={self.id} name='{self.name}'>"


class HabitCompletion(Base, APISerializable):
    """Stores each completion as a new entry, enabling better analytics."""

    habit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("habits.id"), nullable=False
    )

    user = relationship("User", back_populates="habit_completion")
    habit = relationship("Habit", back_populates="habit_completions")

    def __repr__(self) -> str:
        return f"<HabitCompletion id={self.id} habit_id={self.habit_id}>"


# NOTE: Unsure about this placement
class LeetCodeRecord(Base, APISerializable):
    leetcode_id: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String(LC_TITLE_MAX_LENGTH))

    difficulty: Mapped[DifficultyEnum] = mapped_column(
        SAEnum(DifficultyEnum, name="difficulty_enum"), nullable=False
    )

    language: Mapped[LanguageEnum] = mapped_column(
        SAEnum(LanguageEnum, name="language_enum"), nullable=False
    )

    status: Mapped[LCStatusEnum] = mapped_column(
        SAEnum(LCStatusEnum, name="lcstatus_enum"), nullable=False
    )

    user = relationship("User", back_populates="leet_code_record")

    def __repr__(self) -> str:
        return f"<LeetCodeRecord id={self.id} title='{self.title}'>"
