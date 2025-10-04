"""
AuthRepository class doesn't make sense here yet, but will add for some useful "post-auth" operations.
"""
from sqlalchemy import select

from app.modules.auth.models import User, UserLangEnum, UserRoleEnum


class UsersRepository:
    def __init__(self, session):
        self.session = session

    def add_user(self, user: User):
        return self.session.add(user)


    def create_user(self, username: str, password: str, name: str | None,
                    role: UserRoleEnum, lang: UserLangEnum):
        user = User(
            username=username,
            password=password,
            name=name,
            role=role.value,
            lang=lang.value
        )
        user.hash_password(password)
        return self.session.add(user)


    def get_user_by_username(self, username: str):
        return self.session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()

    def get_user_by_user_id(self, user_id: int):
        return self.session.get(User, int(user_id))
