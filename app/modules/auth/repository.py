"""
AuthRepository class doesn't make sense here yet, but will add for some useful "post-auth" operations.
"""
from sqlalchemy import select

from app.modules.auth.models import User, UserLangEnum, UserRoleEnum


class UsersRepository:
    def __init__(self, session):
        self.session = session

    def create_user(self, username: str, password: str, name: str | None,
                    role: UserRoleEnum, lang: UserLangEnum):
        user = User(
            username=username,
            name=name,
            role=role.value,
            lang=lang.value
        )
        user.hash_password(password)
        return self.session.add(user)

    def get_user_by_username(self, username: str):
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_user_by_user_id(self, user_id: int):
        stmt = select(User).where(User.id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()
