# Storing daily API call count because I'm paranoid & hate surprise bills

from sqlalchemy import Column, Date, Integer, String, UniqueConstraint

from app._infra.db_base import Base


class ApiCallRecord(Base):
    user_id = None # Override BaseModel auto-add, TODO: Find better solution
    api_called = Column(String(255), nullable=False)
    date = Column(Date, nullable=False) # Just date
    call_count = Column(Integer, server_default='0')

    __table_args__ = (UniqueConstraint('api_called', 'date'),) # "the combination of api_called AND date together must be unique"