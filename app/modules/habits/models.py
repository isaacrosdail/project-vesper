"""
Model definitions for Habits module.
"""
import enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app._infra.db_base import Base

# Association table
habit_tags = Table(
    "habit_tags",
    Base.metadata,
    Column("habit_id", ForeignKey("habit.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

class Status(enum.Enum):
    experimental = "experimental"
    established = "established"

class LCStatus(enum.Enum):
    SOLVED = "solved"
    ATTEMPTED = "attempted"
    REVIEWED = "reviewed"

class Difficulty(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Language(enum.Enum):
    PYTHON = "Python"
    JS = "JavaScript"
    CPP = "C++"
    C = "C"

class Habit(Base):

    habit_completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")

    name = Column(String(255), unique=True, nullable=False)
    status = Column(SAEnum(Status), default=Status.experimental, nullable=False)
    established_date = Column(DateTime(timezone=True), nullable=True)
    promotion_threshold = Column(Float, default=0.7)
    
    tags = relationship("Tag", secondary=habit_tags, back_populates="habits")

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<Habit id={self.id} name='{self.name}'>"


# Habit Completion Model - enables us to track WHEN and HOW OFTEN specific habits were completed!
# Stores each "completion" as a new entry
class HabitCompletion(Base):
    habit = relationship("Habit", back_populates="habit_completions")

    habit_id = Column(Integer, ForeignKey('habit.id'))


## Uncertain about this placement, but keeps things logically consistent for now
class LeetCodeRecord(Base):
    leetcode_id = Column(Integer, nullable=False)
    title = Column(String(255))
    difficulty = Column(SAEnum(Difficulty), default=Difficulty.MEDIUM, nullable=False)
    language = Column(SAEnum(Language), default=Language.PYTHON, nullable=False)
    status = Column(SAEnum(LCStatus), default=LCStatus.SOLVED, nullable=False)