
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.shared.target import Target, TargetKind


class APISchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class APIReadSchema(BaseModel):
    # from_attributes=True is what makes TaskRead.model_validate(task) read the ORM obj
    # it uses getattr, so plain cols, the is_done hybrid prop, and subtype property all come with for free
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def dump(cls, obj: Any) -> dict[str, Any]:
        return cls.model_validate(obj).model_dump(mode="json")


class PillarRead(APIReadSchema):
    id: int
    name: str # TODO: should be a literal union of the 5 we use?

class TargetRead(APIReadSchema):
    low: float | None
    high: float | None
    nominal: float | None
    threshold: float | None
    kind: TargetKind | None

class AtLeastCreate(APISchema):
    kind: Literal["at_least"]
    value: float = Field(gt=0)

    def to_domain(self) -> Target:
        return Target.at_least(self.value)

class AtMostCreate(APISchema):
    kind: Literal["at_most"]
    value: float = Field(gt=0)

    def to_domain(self) -> Target:
        return Target.at_most(self.value)

class WithinCreate(APISchema):
    kind: Literal["within"]
    value: float = Field(gt=0)
    tolerance: float = Field(ge=0)

    def to_domain(self) -> Target:
        return Target.within(self.value, self.tolerance)

TargetCreate = Annotated[AtLeastCreate | AtMostCreate | WithinCreate, Field(discriminator="kind")]
