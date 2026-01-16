"""Basic API call limiting helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from sqlalchemy.orm import Session

from sqlalchemy import text


def reserve_slot(
    session: Session, api_name: str, call_date: date, daily_limit: int
) -> int | None:
    """Automatically reserve one API call slot for (api_name, date).
    Returns the reserved_count if reserved, or None if the limit was already reached.
    """
    result = session.execute(
        text("""
            INSERT INTO api_call_records (api_called, date, call_count)
            VALUES (:api, :d, 1)
            ON CONFLICT (api_called, date)
            DO UPDATE SET call_count = api_call_records.call_count + 1
            WHERE api_call_records.call_count < :lmt
            RETURNING call_count
        """),
        {"api": api_name, "d": call_date, "lmt": daily_limit},
    )
    return result.scalar_one_or_none()


def release_slot(session: Session, api_name: str, call_date: date) -> None:
    """Decrements the daily API call count for a given (api_name, call_date) tuple, for undoing
    a reservation after upstream failure.
    """
    session.execute(
        text("""
            UPDATE api_call_records
            SET call_count = GREATEST(api_call_records.call_count - 1, 0)
            WHERE api_called = :a AND date = :d
        """),
        {"a": api_name, "d": call_date},
    )
