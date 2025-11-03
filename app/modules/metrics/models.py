import enum

from sqlalchemy import Column, Numeric, Integer, DateTime, String, ForeignKey, Boolean
from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app._infra.db_base import Base
from app.shared.serialization import APISerializable

from app.modules.metrics.constants import (
    WEIGHT_PRECISION,
    WEIGHT_SCALE,
    WEIGHT_MINIMUM,
    STEPS_MINIMUM,
    CALORIES_MINIMUM,
)

class ABVariantEnum(enum.Enum):
    A = "A"
    B = "B"

class DailyEntry(Base, APISerializable):
    """Stores everything in "master" units (kg, count, kcal), will convert based on user preferences."""

    __table_args__ = (
        CheckConstraint(f'weight > {WEIGHT_MINIMUM}', name='ck_weight_positive'),
        CheckConstraint(f'steps >= {STEPS_MINIMUM}', name='ck_steps_non_negative'),
        CheckConstraint(f'calories >= {CALORIES_MINIMUM}', name='ck_calories_non_negative'),
        Index('ix_user_entry_datetime', 'user_id', 'entry_datetime'),
    )

    entry_datetime = Column(DateTime(timezone=True), nullable=False)

    weight = Column(
        Numeric(WEIGHT_PRECISION, WEIGHT_SCALE),
    )

    steps = Column(Integer)

    calories = Column(Integer)

    wake_time = Column(DateTime(timezone=True))

    sleep_time = Column(DateTime(timezone=True))

    sleep_duration_minutes = Column(Integer)

    def __repr__(self):
        return f"<DailyEntry id={self.id} created_at={self.created_at}>"

    @property
    def populated_metrics(self):
        """Returns list of metrics which have entries."""
        metrics = []
        metric_types = ["weight", "steps", "wake_time", "sleep_time", "calories"]
        # Get corresponding attribute for each column to see if it's populated
        # If yes, store in metrics list
        metrics = [metric_type for metric_type in metric_types if getattr(self, metric_type) is not None]
        return metrics
    
    @property
    def has_sleep_data(self):
        """True if both sleep & wake times are stored."""
        return self.sleep_time is not None and self.wake_time is not None


class ABTest(Base, APISerializable):

    title = Column(String(100), nullable=False)

    hypothesis = Column(String(100), nullable=False)

    variant_a_label = Column(String(50), nullable=False)

    variant_b_label = Column(String(50), nullable=False)

    success_condition = Column(String(50), nullable=False)

    trials = relationship("ABTrial", back_populates="ab_test", cascade="all, delete-orphan")

class ABTrial(Base, APISerializable):

    abtest_id = Column(Integer, ForeignKey("ab_tests.id"), nullable=False)

    variant = Column(SAEnum(ABVariantEnum), nullable=False)

    is_success = Column(Boolean(), nullable=True)

    notes = Column(String(200), nullable=True)

    ab_test = relationship("ABTest", back_populates="trials")