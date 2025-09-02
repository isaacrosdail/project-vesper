"""
Service layer for API module. Currently housing our API call limiting helpers.
"""
from sqlalchemy import text


# Atomically increment count if < limit
# Returns new count (if reserved) or None (if limit reached)
def reserve_slot(session, api_name: str, date, daily_limit: int):
    """
    Automatically reserve one API call slot for (api_name, date).
    Returns the reserved_count if reserved, or None if the limit was already reached.
    """
    # Postgres-specific, but one time won't hurt
    result = session.execute(
        text("""
            INSERT INTO apicallrecord (api_called, date, call_count)
            VALUES (:api, :d, 1)
            ON CONFLICT (api_called, date)
            DO UPDATE SET call_count = apicallrecord.call_count + 1
            WHERE apicallrecord.call_count < :lmt
            RETURNING call_count
        """),
        {"api": api_name, "d": date, "lmt": daily_limit}
    )
    return result.scalar_one_or_none()


def release_slot(session, api_name: str, date) -> None:
    """Return a previously reserved slot after a failed upstream call."""
    session.execute(
        text("""
            UPDATE apicallrecord
            SET call_count = GREATEST(apicallrecord.call_count - 1, 0)
            WHERE api_called = :a AND date = :d
        """), 
        {"a": api_name, "d": date}
    )