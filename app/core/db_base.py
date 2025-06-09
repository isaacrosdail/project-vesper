from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import Column, Integer, DateTime, Boolean
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class CustomBase:
    id = Column(Integer, primary_key=True) # Consider upping to UUIDs later
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Now auto-gen tablenames (note: singular now ofc)
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    # Applying our "virtual attribute" from Task model to our Base class here so any model can use it
    # @property is a common decorator for creating "virtual attributes" that are computed on-the-fly
    # Lets us convert to London time simply by doing task.created_at_local
    # as if it were a column in the model itself
    @property
    def created_at_local(self):
        return self.created_at.astimezone(ZoneInfo("Europe/London"))
    
    # Also add one for updated_at! (if it exists)
    @property
    def updated_at_local(self):
        return self.updated_at.astimezone(ZoneInfo("Europe/London")) if self.updated_at else None

# Define base class for models
Base = declarative_base(cls=CustomBase)

# Mixin -> no Base, no CustomBase parent, just pure mixin
# Will attach to HabitCompletion & Task for now (moving to TaskCompletion can be a potential task for future self!)
class CustomBaseTaskMixin:
    completed_at =  Column(DateTime(timezone=True), nullable=True)