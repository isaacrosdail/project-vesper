from enum import StrEnum, auto
from dataclasses import dataclass
from typing import ClassVar, assert_never

# TODO: trying this out


# class TargetKind(StrEnum):
#     AT_LEAST = auto()  # steps
#     AT_MOST = auto()   # sodium?
#     WITHIN = auto()    # calories, sleep, weight

class TargetStatus(StrEnum):
    GOOD = auto()
    OVER = auto()
    UNDER = auto()

@dataclass(frozen=True)
class AtLeast:
    kind: ClassVar[str] = "at_least"
    value: float

@dataclass(frozen=True)
class AtMost:
    kind: ClassVar[str] = "at_most"
    value: float

@dataclass(frozen=True)
class Within:
    """Tolerance is plain value (eg 10 with tolerance 2 means 8-12)"""
    kind: ClassVar[str] = "within"
    # low: int
    # high: int
    value: float
    tolerance: float

Target = AtLeast | AtMost | Within

def is_met(target: Target, value: float) -> bool:
    return target_status(target, value) is TargetStatus.GOOD

def target_status(target: Target, compared_to: float) -> TargetStatus:
    match target:
        case AtLeast(value):
            return TargetStatus.UNDER if compared_to < value else TargetStatus.GOOD
        case AtMost(value):
            return TargetStatus.OVER if compared_to > value else TargetStatus.GOOD
        case Within(value, tolerance):
            if compared_to < (value - tolerance): return TargetStatus.UNDER
            if compared_to > (value + tolerance): return TargetStatus.OVER
            return TargetStatus.GOOD
        case _:
            assert_never(target)

## TODO: remove? bypassed anyway, and replaced by Pydantic schema TargetRead
def serialize_target(target: Target) -> dict[str, str | int | float]:
    match target:
        case AtLeast(value):
            return { "kind": "at_least", "value": value }
        case AtMost(value):
            return { "kind": "at_most", "value": value }
        case Within(value, tolerance):
            # return { "kind": "within", "low": low, "high": high }
            return { "kind": "within", "value": value, "tolerance": tolerance }
        case _: assert_never(target)
