
from sqlalchemy import Column, Numeric, Integer, DateTime
from sqlalchemy import CheckConstraint

from app._infra.db_base import Base

from app.modules.metrics.constants import (
    WEIGHT_PRECISION,
    WEIGHT_SCALE,
    WEIGHT_MINIMUM,
    STEPS_MINIMUM,
    CALORIES_MINIMUM,
)


class DailyEntry(Base):
    """Stores everything in "master" units (kg, count, kcal), will convert based on user preferences."""

    weight = Column(
        Numeric(WEIGHT_PRECISION, WEIGHT_SCALE),
        CheckConstraint(f'weight > {WEIGHT_MINIMUM}', name='ck_weight_positive')
    )

    steps = Column(
        Integer,
        CheckConstraint(f'steps >= {STEPS_MINIMUM}', name='ck_steps_non_negative')
    )

    calories = Column(
        Integer,
        CheckConstraint(f'calories >= {CALORIES_MINIMUM}', name='ck_calories_non_negative')
    )

    wake_time = Column(DateTime(timezone=True))

    sleep_time = Column(DateTime(timezone=True))


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