from datetime import date, datetime
from typing import Literal, Self

from pydantic import Field, model_validator, AwareDatetime

from app.modules.metrics.models import MetricType, WeightUnitsEnum
from app.shared.schemas import APIReadSchema, APISchema


class DailyMetricsCreate(APISchema):
    entry_date: date
    weight: float | None = Field(default=None, gt=0)
    weight_units: WeightUnitsEnum | None = None
    steps: int | None = Field(default=None, gt=0)
    calories: int | None = Field(default=None, ge=0)
    wake_datetime: AwareDatetime | None = None
    sleep_datetime: AwareDatetime | None = None

    @model_validator(mode="after")
    def require_weight_and_units_together(self) -> Self:
        if (self.weight is None) != (self.weight_units is None):
            raise ValueError("Weight entry requires accompanying weight_units value")
        return self

    @model_validator(mode="after")
    def require_at_least_one_metric(self) -> Self:
        metrics = (self.weight, self.weight_units, self.steps, self.calories,
                   self.wake_datetime, self.sleep_datetime)
        if all(m is None for m in metrics):
            raise ValueError("At least one metric is required")
        return self


class DailyMetricsRead(APIReadSchema):
    id: int
    entry_datetime: datetime
    weight: float | None
    steps: int | None
    calories: int | None
    wake_datetime: datetime | None
    sleep_datetime: datetime | None
    sleep_duration_minutes: int | None
    created_at: datetime
    subtype: Literal['daily_metrics']


class DailyMetricsPointRead(APISchema):
    date: datetime
    value: float | None


class MetricsWindowQuery(APISchema):
    lastNDays: int = Field(gt=0)
    metric_type: MetricType | None = None
