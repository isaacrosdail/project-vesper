# Defines our core Mixins as well as our BaseModel & declarative Base

from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Core mixins
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
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

# Base Model
class BaseModel:
    id = Column(Integer, primary_key=True) # Consider upping to UUIDs later

    # Autogenerate table names (singular)
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    # Only add user_id FKey if this isn't the User model
    @declared_attr
    def user_id(cls):
        if cls.__name__ != 'User':
            return Column(Integer, ForeignKey('user.id'), nullable=False, default=1)

# Define base class for models
# Now all classes using (Base) receive IDs, a user.id FKey (except User), & Timestamp info
Base = declarative_base(cls=BaseModel, mixins=(TimestampMixin,))

# Mixin -> no Base, no CustomBase parent, just pure mixin
# Will attach to HabitCompletion & Task for now (moving to TaskCompletion can be a potential task for future self!)
class CustomBaseTaskMixin:
    completed_at =  Column(DateTime(timezone=True), nullable=True)