# Rate limit helpers

from app._infra.database import database_connection
from sqlalchemy import text


# Atomically increment count if < limit
# Returns new count (if reserved) or None (if limit reached)
def reserve_slot(api_name: str, date, daily_limit: int):
        """
        Automatically reserve one API call slot for (api_name, date).
        Returns the reserved_count if reserved, or None if the limit was already reached.
        """
        # Postgres-specific, but one time won't hurt
        with database_connection() as session:
            result = session.execute(
                text("""
                    INSERT INTO apicallrecord (api_called, date, call_count)
                    VALUES (:api_name, :date, 1)
                    ON CONFLICT (api_called, date)
                    DO UPDATE SET call_count = apicallrecord.call_count + 1
                    WHERE apicallrecord.call_count < :limit
                    RETURNING call_count
                """),
                {"api_name": api_name, "date": date, "limit": daily_limit}
            )
            return result.scalar_one_or_none()

# Decrement count by 1 upon failure
def release_slot(api_name: str, date) -> None:
    """Return a previously reserved slot after a failed upstream call."""
    with database_connection() as session:
        session.execute(
            text(f"""
                UPDATE apicallrecord
                SET apicallrecord.call_count = GREATEST(apicallrecord.call_count - 1, 0)
                WHERE api_called = :a AND date = :d
            """), 
            {"a": api_name, "d": date}
        )