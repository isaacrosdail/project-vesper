"""
Defines our core Mixins as well as our BaseModel & declarative Base.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import current_app
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, declared_attr


# Core mixins
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    
    # Provides timezone-localized timestamp properties for template use
    @property
    def created_at_local(self):
        tzname = current_app.config.get("DEFAULT_TZ", "Europe/London")
        return self.created_at.astimezone(ZoneInfo(tzname))
    
    @property
    def updated_at_local(self):
        tzname = current_app.config.get("DEFAULT_TZ", "Europe/London")
        return self.updated_at.astimezone(ZoneInfo(tzname)) if self.updated_at else None

# Base Model (inherits timestamp info)
class BaseModel(TimestampMixin):
    id = Column(Integer, primary_key=True)

    # Autogenerate table names (singular) from class names
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    # Automatically add user_id FKey to all models except User & ApiCallRecord (latter is global for internal use)
    @declared_attr
    def user_id(cls):
        if cls.__name__ not in ['User', 'ApiCallRecord']:
            return Column(Integer, ForeignKey('user.id'), nullable=False)

# SQLAlchemy declarative base with automatic timestamps & user association
Base = declarative_base(cls=BaseModel)

# Mixin for models that track completion status (unsure about this one)
class CustomBaseTaskMixin:
    completed_at =  Column(DateTime(timezone=True), nullable=True)