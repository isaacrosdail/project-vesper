from app._infra.database import db_session
from app.modules.auth.models import User


def test_user_clearing(app, logged_in_user):
    assert logged_in_user.username.startswith("Test_username")

    # check user exists in db
    all_users = db_session.query(User).all()
    assert len(all_users) == 1

def test_second_user_test(logged_in_user):

    # if clear_tables works, this should too
    all_users = db_session.query(User).all()
    assert len(all_users) == 1