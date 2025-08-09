# Storing daily API call count because I'm paranoid & hate surprise bills

from sqlalchemy import Column, Integer, String, Date, UniqueConstraint
from app.core.db_base import Base

class ApiCallRecord(Base):
    user_id = None # Override BaseModel auto-add, TODO: Find better solution
    api_called = Column(String(255), nullable=False)
    date = Column(Date, nullable=False) # Just date
    call_count = Column(Integer, default=0)
    # Composite uniqueness => "1 API call PER API PER day"
    __table_args__ = (UniqueConstraint('api_called', 'date'),)