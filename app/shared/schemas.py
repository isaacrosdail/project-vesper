
from typing import Any

from pydantic import BaseModel, ConfigDict


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
