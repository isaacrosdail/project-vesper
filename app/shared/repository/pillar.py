from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


from app.shared.models import Pillar
from app.shared.repository.base import BaseRepository


class PillarRepository(BaseRepository[Pillar]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Pillar)

