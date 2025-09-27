# Storing daily API call count because I'm paranoid & hate surprise bills

from sqlalchemy import Column, Date, Integer, String, UniqueConstraint

from app._infra.db_base import Base


class ApiCallRecord(Base):

    __table_args__ = (
        UniqueConstraint('api_called', 'date', name='uq_api_called_date'), # "the combination of api_called AND date together must be unique"
    )

    # NOTE: Override BaseModel auto-add, TODO: Find better solution
    user_id = None
    api_called = Column(String(255), nullable=False)
    date = Column(Date, nullable=False) # Just date
    call_count = Column(Integer, server_default='0')
