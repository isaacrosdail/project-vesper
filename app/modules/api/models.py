# Storing daily API call count because I'm paranoid & hate surprise bills

from app._infra.db_base import Base
from sqlalchemy import Column, Date, Integer, String, UniqueConstraint


class ApiCallRecord(Base):
    user_id = None # Override BaseModel auto-add, TODO: Find better solution
    api_called = Column(String(255), nullable=False)
    date = Column(Date, nullable=False) # Just date
    call_count = Column(Integer, default=0)
    # TODO: NOTES: Add notes for this: Composite unique constraint => "1 API call PER API PER day"
    # Postgres ON CONFLICT
    # So "The combination of api_called AND date together must be unique"
    __table_args__ = (UniqueConstraint('api_called', 'date'),)