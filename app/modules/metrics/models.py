from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.modules.metrics.validation_constants import (
    CALORIES_MINIMUM,
    STEPS_MINIMUM,
    WEIGHT_MINIMUM,
)
from app.shared.datetime_.helpers import convert_to_timezone
from app.shared.serialization import APISerializable


class DailyMetrics(Base, APISerializable):
    """Stores everything in "master" units (kg, count, kcal)."""

    __tablename__ = "daily_metrics"

    __table_args__ = (
        CheckConstraint(f"weight > {WEIGHT_MINIMUM}", name="ck_weight_positive"),
        CheckConstraint(f"steps >= {STEPS_MINIMUM}", name="ck_steps_non_negative"),
        CheckConstraint(
            f"calories >= {CALORIES_MINIMUM}", name="ck_calories_non_negative"
        ),
        Index("ix_user_entry_datetime", "user_id", "entry_datetime"),
    )

    entry_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    weight: Mapped[float] = mapped_column(Float, nullable=True)

    steps: Mapped[int] = mapped_column(Integer, nullable=True)

    calories: Mapped[int] = mapped_column(Integer, nullable=True)

    wake_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    sleep_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    sleep_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=True)

    @property
    def entry_datetime_local(self) -> datetime:
        return convert_to_timezone(self.user.timezone, self.entry_datetime)

    @property
    def wake_datetime_local(self) -> datetime | None:
        return (
            convert_to_timezone(self.user.timezone, self.wake_datetime)
            if self.wake_datetime
            else None
        )

    @property
    def sleep_datetime_local(self) -> datetime | None:
        return (
            convert_to_timezone(self.user.timezone, self.sleep_datetime)
            if self.sleep_datetime
            else None
        )

    user = relationship("User", back_populates="daily_metrics")

    def __repr__(self) -> str:
        return f"<DailyMetrics id={self.id} created_at={self.created_at}>"

    @property
    def populated_metrics(self) -> list[str]:
        """Returns list of daily metrics which have entries."""
        metric_types = {"weight", "steps", "wake_datetime", "sleep_datetime", "calories"}
        return [
            metric_type
            for metric_type in metric_types
            if getattr(self, metric_type) is not None
        ]

    @property
    def has_sleep_data(self) -> bool:
        """True if both sleep & wake times are stored."""
        return self.sleep_datetime is not None and self.wake_datetime is not None
