"""Track daily API call counts to monitor usage."""

from datetime import date as DateType

from sqlalchemy import Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app._infra.db_base import Base


class ApiCallRecord(Base):
    __table_args__ = (
        UniqueConstraint("api_called", "date", name="uq_api_called_date"),
    )

    api_called: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[DateType] = mapped_column(Date, nullable=False)  # Just date
    call_count: Mapped[int] = mapped_column(Integer, server_default="0")
