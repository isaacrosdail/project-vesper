from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

cases = ["", "postgresql://", "postgresql://u@:5432/db", "postgresql://u:p@host:bad/db", "not a url", "sqlite:///x.db"]

for s in cases:
    try:
        u = make_url(s)
        print("OK   ", s, "->", u.render_as_string(hide_password=True))
    except Exception as e:
        print("FAIL ", s, type(e).__name__, str(e)[:120])


# Masks DB password in debug output
def _safe_db_uri(uri: str) -> str:
    """Mask database password in debug output."""
    try:
        return make_url(uri).render_as_string(hide_password=True)
    except Exception:
        return uri