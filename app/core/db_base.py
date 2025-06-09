from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import Column, Integer, DateTime, Boolean
from datetime import datetime, timezone

class CustomBase:
    id = Column(Integer, primary_key=True) # Consider upping to UUIDs later
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    
    # Now auto-gen tablenames (note: singular now ofc)
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

# Define base class for models
Base = declarative_base(cls=CustomBase)

# Mixin -> no Base, no CustomBase parent, just pure mixin
# Will attach to HabitCompletion & Task for now (moving to TaskCompletion can be a potential task for future self!)
class CustomBaseTaskMixin:
    completed_at =  Column(DateTime(timezone=True), nullable=True)