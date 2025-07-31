from app.core.auth.models import User

def get_user_by_username(username: str, session):
    return session.query(User).filter_by(username=username).one_or_none()