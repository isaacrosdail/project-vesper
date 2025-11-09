"""
Model definitions for Habits module.
"""
import enum
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.modules.habits.constants import (HABIT_NAME_MAX_LENGTH,
                                          LC_TITLE_MAX_LENGTH,
                                          PROMOTION_THRESHOLD_MAX,
                                          PROMOTION_THRESHOLD_MIN)
from app.shared.models import Tag, habit_tags
from app.shared.serialization import APISerializable


class StatusEnum(enum.Enum):
    EXPERIMENTAL = "EXPERIMENTAL"
    ESTABLISHED = "ESTABLISHED"

class LCStatusEnum(enum.Enum):
    SOLVED = "SOLVED"
    ATTEMPTED = "ATTEMPTED"
    REVIEWED = "REVIEWED"

class DifficultyEnum(enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class LanguageEnum(enum.Enum):
    PYTHON = "PYTHON"
    JS = "JS"
    CPP = "CPP"
    C = "C"

class Habit(Base, APISerializable):

    __api_exclude__: list[str] = []

    # Use super() to "append to" our serializer's result dict to add derived keys
    def to_api_dict(self) -> Any:
        result = super().to_api_dict()
        result["is_promotable"] = (
            self.status is not None
            and self.promotion_threshold is not None
        )
        return result

    __table_args__ = (
        CheckConstraint(
            f'promotion_threshold is NULL OR (promotion_threshold >= {PROMOTION_THRESHOLD_MIN} AND promotion_threshold <= {PROMOTION_THRESHOLD_MAX})', name='ck_promotion_threshold_range_0_1'
        ),
        UniqueConstraint('user_id', 'name', name='uq_user_habit_name'),
    )

    name: Mapped[str] = mapped_column(
        String(HABIT_NAME_MAX_LENGTH),
        nullable=False
    )

    status: Mapped[StatusEnum] = mapped_column(
        SAEnum(StatusEnum, name="status_enum"),
        nullable=True
    )

    established_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    promotion_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=True
    )
    
    tags = relationship("Tag", secondary=habit_tags, back_populates="habits")
    habit_completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"<Habit id={self.id} name='{self.name}'>"


class HabitCompletion(Base, APISerializable):
    """Stores each completion as a new entry, enabling better analytics."""

    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey('habits.id'), nullable=False)
    
    habit = relationship("Habit", back_populates="habit_completions")

    def __repr__(self) -> str:
        return f"<HabitCompletion id={self.id} habit_id={self.habit_id}>"

# NOTE: Unsure about this placement
class LeetCodeRecord(Base, APISerializable):

    leetcode_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    title: Mapped[str] = mapped_column(String(LC_TITLE_MAX_LENGTH))

    difficulty: Mapped[DifficultyEnum] = mapped_column(
        SAEnum(DifficultyEnum, name="difficulty_enum"),
        nullable=False
    )

    language: Mapped[LanguageEnum] = mapped_column(
        SAEnum(LanguageEnum, name="language_enum"),
        nullable=False
    )

    status: Mapped[LCStatusEnum] = mapped_column(
        SAEnum(LCStatusEnum, name="lcstatus_enum"),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<LeetCodeRecord id={self.id} title='{self.title}'>"