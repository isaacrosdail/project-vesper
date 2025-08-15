from app.modules.auth.models import User

# Helpers to DRY things up
def create_demo_user(session, username="guest", name="Guest", password="demo123"):
    user = User(username=username, name=name, role="user")
    user.set_password(password)
    session.add(user)
    return user

def create_owner_user(session, username="owner", name="owner", password="owner123"):
    user = User(username=username, name=name, role="owner")
    user.set_password(password)
    session.add(user)
    return user

# Note to self: .filter_by() takes column names are keyword args (column_name=value)
def get_user_by_username(username: str, session):
    """
    Get user by username from Users table.
    Args:
        username (str): Username to search for.
        session (Session): An active SQLAlchemy session.
    Returns:
        User | None: The matching User object if found, otherwise None.
    """
    return session.query(User).filter_by(username=username).one_or_none()

def get_user_by_user_id(user_id: int, session):
    return session.get(User, int(user_id))