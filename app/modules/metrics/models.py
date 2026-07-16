from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy import CheckConstraint, DateTime, Float, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.shared.datetime_.helpers import convert_to_timezone


class WeightUnitsEnum(StrEnum):
    LBS = auto()
    KG = auto()


# TODO: prob doesnt belong here?
from typing import Literal

MetricType = Literal["weight", "steps", "calories", "sleep_duration_minutes"]


class DailyMetrics(Base):
    """Stores everything in "master" units (kg, count, kcal)."""

    __tablename__ = "daily_metrics"

    __table_args__ = (
        CheckConstraint("weight > 0", name="weight_positive"),
        CheckConstraint("steps >= 0", name="steps_non_negative"),
        CheckConstraint("calories >= 0", name="calories_non_negative"),
        Index("ix_user_entry_datetime", "user_id", "entry_datetime"),
    )

    entry_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    weight: Mapped[float | None] = mapped_column(Float, nullable=True)

    # weight_units: Mapped[WeightUnitsEnum | None] = mapped_column(
    #     SAEnum(WeightUnitsEnum, name="weight_units_enum", values_callable=lambda x: [e.value for e in x]),
    #     nullable=True
    # )

    steps: Mapped[int | None] = mapped_column(Integer, nullable=True)

    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)

    wake_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    sleep_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    sleep_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

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
