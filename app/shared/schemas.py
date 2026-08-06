
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


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


class AtLeastRead(APIReadSchema):
    kind: Literal["at_least"]
    value: float

class AtMostRead(APIReadSchema):
    kind: Literal["at_most"]
    value: float

class WithinRead(APIReadSchema):
    kind: Literal["within"]
    value: float
    tolerance: float

    @computed_field # type: ignore[prop-decorator]
    @property
    def low(self) -> float:
        return self.value - self.tolerance

    @computed_field # type: ignore[prop-decorator]
    @property
    def high(self) -> float:
        return self.value + self.tolerance

TargetRead = Annotated[AtLeastRead | AtMostRead | WithinRead, Field(discriminator="kind")]

class AtLeastCreate(APISchema):
    kind: Literal["at_least"]
    value: float = Field(gt=0)

class AtMostCreate(APISchema):
    kind: Literal["at_most"]
    value: float = Field(gt=0)

class WithinCreate(APISchema):
    kind: Literal["within"]
    value: float = Field(gt=0)
    tolerance: float = Field(gt=0)

TargetCreate = Annotated[AtLeastCreate | AtMostCreate | WithinCreate, Field(discriminator="kind")]
