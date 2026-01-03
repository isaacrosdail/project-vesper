
from datetime import datetime
from decimal import Decimal
import enum

from sqlalchemy import Column, Numeric, Integer, DateTime, String, ForeignKey, Boolean
from sqlalchemy import CheckConstraint, Index
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

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

    entry_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    weight: Mapped[Decimal] = mapped_column(
        Numeric(WEIGHT_PRECISION, WEIGHT_SCALE),
    )

    steps: Mapped[int] = mapped_column(Integer)

    calories: Mapped[int] = mapped_column(Integer)

    wake_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    sleep_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    sleep_duration_minutes: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<DailyEntry id={self.id} created_at={self.created_at}>"

    @property
    def populated_metrics(self) -> list[str]:
        """Returns list of metrics which have entries."""
        metrics = []
        metric_types = ["weight", "steps", "wake_time", "sleep_time", "calories"]
        # Get corresponding attribute for each column to see if it's populated
        # If yes, store in metrics list
        metrics = [metric_type for metric_type in metric_types if getattr(self, metric_type) is not None]
        return metrics
    
    @property
    def has_sleep_data(self) -> bool:
        """True if both sleep & wake times are stored."""
        return self.sleep_time is not None and self.wake_time is not None
