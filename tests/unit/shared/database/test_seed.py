
from sqlalchemy import inspect
from sqlalchemy.future import select

# from app._infra.database import db_sessio
from app.shared.database.seed.seed_db import Level, Performance, seed_rich_data
from app.shared.models import Pillar
from tests.unit.shared.database.test_database_helpers import row_count_by_table


def test_thing(session, logged_in_user):
    # seed_pillars(session, logged_in_user.id)
    pillars = {p.name: p for p in session.scalars(select(Pillar).where(Pillar.user_id==logged_in_user.id))}
    objs = seed_rich_data(pillars, logged_in_user.id, Level.BASIC, Performance.AVERAGE)

    # inspect(obj).transient -> Python objs only, not yet in session via add
    #   session.new is empty
    # assert all([inspect(o).transient for o in objs])
    for o in objs: assert inspect(o).transient, f"{o!r} is not transient"
    session.add_all(objs)
    # inspect(obj).pending  -> "staged": added to ??? but not yet flushed or committed
    # ie when we add via relationship instead of ids (since they dont exist yet at this stage),
    #   habit.id is None etc
    #  objs are now setting in session.new
    assert all([inspect(o).pending for o in objs])
    session.flush()
    # inspect(obj).persistent -> habit_id is now an int, and it matches habit.id
    assert all([inspect(o).persistent for o in objs])

    ## get count per table for funsies
    a = row_count_by_table(session, logged_in_user.id)


## Testing distributions?
def test_nah():
    from app.shared.utils import clamp
    a = 11
    b = 4
    assert clamp(a, 0, 1) == 1
    assert clamp(b, 4, 10) == 4
    assert clamp(-1, -3, 4) == -1

