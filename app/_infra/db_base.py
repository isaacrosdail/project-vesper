"""Defines our core Mixins as well as our BaseModel & declarative Base."""

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import regex
from flask import current_app
from flask_login import current_user
from sqlalchemy import DateTime, ForeignKey, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

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
    """Adds created_at and updated_at timestamps to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def created_at_local(self) -> datetime:
        """Returns `created_at` in user's local timezone."""
        tzname = current_app.config.get(current_user.timezone, "America/Chicago")
        return self.created_at.astimezone(ZoneInfo(tzname))

    @property
    def updated_at_local(self) -> datetime | None:
        """Returns `updated_at` in user's local timezone (or `None`)."""
        tzname = current_app.config.get(current_user.timezone, "America/Chicago")
        return self.updated_at.astimezone(ZoneInfo(tzname)) if self.updated_at else None


class CustomBaseTaskMixin:
    """Adds completed_at timestamp to task-like models. (unsure about this one)"""
    completed_at: Mapped[datetime] =  mapped_column(DateTime(timezone=True), nullable=True)


class Base(TimestampMixin, DeclarativeBase):
    """Base class for all models. Auto-timestamps, user association, table naming."""

    metadata = metadata

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Autogenerate pluralized, snake_case table names from class names
    # @declared_attr that returns something other than a col/relationship descriptor -> use .directive
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # First regex pass handles 'ABTest' -> 'ab_test'
        name = regex.sub('([A-Z]+)([A-Z][a-z])', r'\1_\2', cls.__name__)
        name = regex.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower() # camelCase -> snake_case first
        # Pluralize
        if name.endswith('y') and name[-2] not in 'aeiou':
            return name[:-1] + 'ies'
        else:
            return name + 's'
    
    # Automatically add user_id FKey to all models except User & ApiCallRecord (latter is global for internal use)
    @declared_attr.directive
    def user_id(cls) -> Mapped[Any]:
        """Automatically adds `user_id` foreign key to all models except: `User`, `ApiCallRecord`."""
        if cls.__name__ not in ["User", "ApiCallRecord"]:
            return mapped_column(
                Integer,
                ForeignKey(
                    "users.id", ondelete="CASCADE"
                ),  # so that deleting a user will auto-delete their tasks/etc?
                nullable=False,
            )
        return None  # type: ignore[return-value]
