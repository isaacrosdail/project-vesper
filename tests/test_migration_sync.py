# tests/test_migration_sync.py
from alembic.config import Config
import pytest
import sqlalchemy as sa
from app._infra.db_base import Base
from alembic import command
import os



def _metadata_names() -> dict[str, set[str]]:
    """What the models say each table's constraint/index names should be."""
    out = {}
    for table in Base.metadata.tables.values():
        names = {str(c.name) for c in table.constraints if c.name}
        names |= {i.name for i in table.indexes}
        out[table.name] = names
    return out

def _db_names(engine) -> dict[str, set[str]]:
    """What actually exists after alembic upgrade head."""
    insp = sa.inspect(engine)
    out = {}
    for t in insp.get_table_names():
        if t == "alembic_version":
            continue
        names = {c["name"] for c in insp.get_check_constraints(t)}
        names |= {c["name"] for c in insp.get_unique_constraints(t)}
        names |= {i["name"] for i in insp.get_indexes(t)}
        names |= {insp.get_pk_constraint(t)["name"]}
        names |= {fk["name"] for fk in insp.get_foreign_keys(t)}
        out[t] = names
    return out

def test_constraint_names_in_sync(migrated_engine):
    expected, actual = _metadata_names(), _db_names(migrated_engine)
    problems = []
    for table in sorted(expected.keys() | actual.keys()):
        missing = expected.get(table, set()) - actual.get(table, set())
        extra = actual.get(table, set()) - expected.get(table, set())
        if missing:
            problems.append(f"{table}: in models but not DB: {sorted(missing)}")
        if extra:
            problems.append(f"{table}: in DB but not models: {sorted(extra)}")
    assert not problems, "\n".join(problems)

@pytest.fixture(scope="session")
def migrated_engine():
    # separate scratch DB so it can't collide with the normal test DB
    admin = sa.create_engine(os.environ.get("TEST_DATABASE_URI"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(sa.text("DROP DATABASE IF EXISTS vesper_migration_test"))
        conn.execute(sa.text("CREATE DATABASE vesper_migration_test"))

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", os.environ.get("TEST_DATABASE_URI"))
    command.upgrade(cfg, "head")

    engine = sa.create_engine(os.environ.get("TEST_DATABASE_URI"))
    yield engine
    engine.dispose()
