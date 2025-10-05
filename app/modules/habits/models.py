"""
Model definitions for Habits module.
"""
import enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, CheckConstraint, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app._infra.db_base import Base
from app.shared.models import Tag, habit_tags

from app.modules.habits.constants import (
    HABIT_NAME_MAX_LENGTH,
    LC_TITLE_MAX_LENGTH,
    PROMOTION_THRESHOLD_DEFAULT,
    PROMOTION_THRESHOLD_MIN,
    PROMOTION_THRESHOLD_MAX,
)


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

class Habit(Base):

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_habit_name'),
    )

    name = Column(
        String(HABIT_NAME_MAX_LENGTH),
        nullable=False
    )

    status = Column(
        SAEnum(StatusEnum, name="status_enum"),
        nullable=True
    )

    established_date = Column(DateTime(timezone=True), nullable=True)

    promotion_threshold = Column(
        Float,
        CheckConstraint(f'promotion_threshold is NULL OR (promotion_threshold >= {PROMOTION_THRESHOLD_MIN} AND promotion_threshold <= {PROMOTION_THRESHOLD_MAX})', name='ck_promotion_threshold_range_0_1'),
        nullable=True
    )
    
    tags = relationship("Tag", secondary=habit_tags, back_populates="habits")
    habit_completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<Habit id={self.id} name='{self.name}'>"


class HabitCompletion(Base):
    """Stores each completion as a new entry, enabling better analytics."""

    habit_id = Column(Integer, ForeignKey('habit.id'), nullable=False)
    
    habit = relationship("Habit", back_populates="habit_completions")

    def __repr__(self):
        return f"<HabitCompletion id={self.id} habit_id={self.habit_id}>"

# NOTE: Unsure about this placement
class LeetCodeRecord(Base):

    leetcode_id = Column(Integer, nullable=False)
    
    title = Column(String(LC_TITLE_MAX_LENGTH))

    difficulty = Column(
        SAEnum(DifficultyEnum, name="difficulty_enum"),
        default=DifficultyEnum.MEDIUM,
        nullable=False
    )

    language = Column(
        SAEnum(LanguageEnum, name="language_enum"),
        default=LanguageEnum.PYTHON,
        nullable=False
    )

    status = Column(
        SAEnum(LCStatusEnum, name="lcstatus_enum"),
        default=LCStatusEnum.SOLVED,
        nullable=False
    )

    def __repr__(self):
        return f"<LeetCodeRecord id={self.id} title='{self.title}'>"