"""
AuthRepository class doesn't make sense here yet, but will add for some useful "post-auth" operations.
"""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.modules.auth.models import User, UserRole


class UsersRepository:
    def __init__(self, session):
        self.session = session

    def add_user(self, user):
        self.session.add(user)
        return user

    def create_demo_user(self,  username="guest", password="demo123", name="Guest"):
        new_user = User(
            username=username,
            name=name,
            role=UserRole.USER.value
        )
        new_user.hash_password(password)
        self.session.add(new_user)
        self.session.flush()
        return new_user
    
    def create_owner_user(self, username="owner", password="owner123", name="Owner"):
        new_owner_user = User(
            username=username,
            name=name,
            role=UserRole.OWNER.value
        )
        new_owner_user.hash_password(password)
        self.session.add(new_owner_user)
        self.session.flush()
        return new_owner_user
    
    def get_user_by_username(self, username: str):
        return self.session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()

    def get_user_by_user_id(self, user_id: int):
        return self.session.get(User, int(user_id))
