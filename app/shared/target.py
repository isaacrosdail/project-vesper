from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto


class TargetKind(StrEnum):
    AT_LEAST = auto()
    AT_MOST = auto()
    WITHIN = auto()

class TargetStatus(StrEnum):
    GOOD = auto()
    OVER = auto()
    UNDER = auto()


@dataclass(frozen=True)
class Target:
    low: float | None = None
    high: float | None = None

    def __post_init__(self) -> None:
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValueError(f"Invalid bounds: low={self.low} > high={self.high}")

    def satisfied(self, compared_to: float) -> bool:
        return self.status(compared_to) is TargetStatus.GOOD

    def status(self, compared_to: float) -> TargetStatus:
        if self.low is not None and compared_to < self.low:
            return TargetStatus.UNDER
        if self.high is not None and compared_to > self.high:
            return TargetStatus.OVER
        return TargetStatus.GOOD

    @classmethod
    def at_least(cls, value: float) -> Target:
        return cls(low=value)

    @classmethod
    def at_most(cls, value: float) -> Target:
        return cls(high=value)

    @classmethod
    def within(cls, value: float, tolerance: float) -> Target:
        return cls(low=value-tolerance, high=value+tolerance)

    @property
    def kind(self) -> TargetKind | None:
        if self.low is not None and self.high is not None:
            return TargetKind.WITHIN
        if self.low is not None:
            return TargetKind.AT_LEAST
        if self.high is not None:
            return TargetKind.AT_MOST
        return None

    @property
    def nominal(self) -> float | None:
        if self.low is not None and self.high is not None:
            return (self.low + self.high) / 2
        return self.low if self.low is not None else self.high

    @property
    def threshold(self) -> float | None:
        return self.low if self.low is not None else self.high
