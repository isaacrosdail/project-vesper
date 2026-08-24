# app/_infra/scoping.py
from flask import has_request_context
from flask_login import current_user
from sqlalchemy import event
from sqlalchemy.orm import with_loader_criteria

from app._infra.database import db_session
from app._infra.db_base import UserScopedMixin


# scoping.py — no Flask imports anymore
@event.listens_for(db_session, "do_orm_execute")
def scope_to_current_user(execute_state):
    if not execute_state.is_select:
        return
    if execute_state.is_column_load or execute_state.is_relationship_load:
        return
    if execute_state.execution_options.get("unscoped", False):
        return

    user_id = execute_state.session.info.get("scoped_user_id")
    if user_id is None:
        return

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(UserScopedMixin, lambda cls: cls.user_id == user_id, include_aliases=True)
    )
