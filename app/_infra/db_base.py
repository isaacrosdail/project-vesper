"""
Defines our core Mixins as well as our BaseModel & declarative Base.
"""
import regex

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import current_app
from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData
from sqlalchemy.orm import declarative_base, declared_attr

# Auto-assigns constraint names when we don't explicitly name them
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

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

    # Autogenerate pluralized, snake_case table names from class names
    @declared_attr
    def __tablename__(cls):
        name = regex.sub('([a-z0-9])([A-Z])', r'\1_\2', cls.__name__).lower() # CamelCase -> snake_case first
        # Pluralize
        if name.endswith('y') and name[-2] not in 'aeiou':
            return name[:-1] + 'ies'
        else:
            return name + 's'
    
    # Automatically add user_id FKey to all models except User & ApiCallRecord (latter is global for internal use)
    @declared_attr
    def user_id(cls):
        if cls.__name__ not in ['User', 'ApiCallRecord']:
            return Column(Integer, ForeignKey('users.id'), nullable=False)

# SQLAlchemy declarative base with automatic timestamps & user association
Base = declarative_base(cls=BaseModel, metadata=metadata)

# Mixin for models that track completion status (unsure about this one)
class CustomBaseTaskMixin:
    completed_at =  Column(DateTime(timezone=True), nullable=True)