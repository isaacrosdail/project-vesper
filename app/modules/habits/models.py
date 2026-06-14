"""
Model definitions for Habits module.
"""

from datetime import datetime, timezone
from enum import StrEnum, auto
from typing import Any, ClassVar

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.shared.datetime_.helpers import convert_to_timezone
from app.shared.models import habit_pillars, habit_tags
from app.shared.serialization import APISerializable

HABIT_NAME_MAX_LENGTH = 100
LC_TITLE_MAX_LENGTH = 200

PROMOTION_THRESHOLD = 0.7 ## TODO: lives here for time being

class StatusEnum(StrEnum):
    EXPERIMENTAL = auto()
    ESTABLISHED = auto()


class LCStatusEnum(StrEnum):
    SOLVED = auto()
    ATTEMPTED = auto()
    REVIEWED = auto()


class DifficultyEnum(StrEnum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

    def __lt__(self, other: str) -> bool:
        order = list(DifficultyEnum)
        return order.index(self) < order.index(DifficultyEnum(other))


class LanguageEnum(StrEnum):
    PYTHON = auto()
    JS = auto()
    CPP = auto()
    C = auto()
    GO = auto()

    @property
    def label(self) -> str:
        labels = {"python": "Python", "js": "JavaScript", "c": "C", "cpp": "C++", "go": "Go"}
        return labels.get(self, self.name.title())


class Habit(Base, APISerializable):
    __api_exclude__: ClassVar[list[str]] = []

    def to_api_dict(self, *, include_relations: bool = True) -> dict[str, Any]:
        result = super().to_api_dict(include_relations=include_relations)
        result["is_promotable"] = self.status is not None
        return result

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_habit_name"),
    )

    name: Mapped[str] = mapped_column(String(HABIT_NAME_MAX_LENGTH), nullable=False)

    status: Mapped[StatusEnum | None] = mapped_column(
        SAEnum(StatusEnum, name="status_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )

    established_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Represents target completion rate per week
    target_frequency: Mapped[int] = mapped_column(Integer, nullable=False)

    @property
    def established_date_local(self) -> datetime | None:
        return (
            convert_to_timezone(self.user.timezone, self.established_date)
            if self.established_date
            else None
        )

    user = relationship("User", back_populates="habits")
    tags = relationship("Tag", secondary=habit_tags, back_populates="habits")
    pillars = relationship("Pillar", secondary=habit_pillars, back_populates="habits", lazy="selectin")
    habit_completions = relationship(
        "HabitCompletion", back_populates="habit", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Habit id={self.id} name='{self.name}'>"


class HabitCompletion(Base, APISerializable):
    """Stores each completion as a new entry, enabling better analytics."""

    __table_args__ = (
        Index("ix_habit_completions_user_habit_completed_at", "user_id", "habit_id", "completed_at"),
    )
    habit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("habits.id"), nullable=False
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    user = relationship("User", back_populates="habit_completion")
    habit = relationship("Habit", back_populates="habit_completions")

    def __repr__(self) -> str:
        return f"<HabitCompletion id={self.id} habit_id={self.habit_id}>"


class LeetCodeRecord(Base, APISerializable):
    __tablename__ = "leetcode_records"

    entry_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    leetcode_id: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str | None] = mapped_column(String(LC_TITLE_MAX_LENGTH), nullable=True)

    difficulty: Mapped[DifficultyEnum] = mapped_column(
        SAEnum(DifficultyEnum, name="difficulty_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    language: Mapped[LanguageEnum] = mapped_column(
        SAEnum(LanguageEnum, name="language_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    status: Mapped[LCStatusEnum] = mapped_column(
        SAEnum(LCStatusEnum, name="lcstatus_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    user = relationship("User", back_populates="leetcode_record")

    def __repr__(self) -> str:
        return f"<LeetCodeRecord id={self.id} title='{self.title}'>"
