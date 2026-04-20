from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.modules.metrics.models import WeightUnitsEnum


class DailyMetricsCreate(BaseModel):
    entry_date: date
    weight: float | None = Field(default=None, gt=0)
    weight_units: WeightUnitsEnum | None = None  # transient, TODO: warrants being an enum? for lbs/kg?
    steps: int | None = Field(default=None, gt=0)
    calories: int | None = Field(default=None, ge=0)
    wake_datetime: datetime | None = None
    sleep_datetime: datetime | None = None

    @model_validator(mode="after")
    def validate_weight_has_units(self) -> Self:
        if self.weight and not self.weight_units:
            raise ValueError("Weight entry requires accompanying weight_units value")
        return self
