from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from app.modules.auth.schemas import UserRegister

if TYPE_CHECKING:

    from sqlalchemy.orm import Session

    from app.modules.auth.repository import UsersRepository

from sqlalchemy.exc import IntegrityError

from app.modules.auth.models import (
    HourCycleEnum,
    UnitSystemEnum,
    User,
    UserGoals,
    UserProfile,
    UserRoleEnum,
)
from app.modules.auth.repository import UsersRepository
from app.shared.database.seed.seed_db import seed_data, seed_pillars
from app.shared.exceptions import ServiceError


class AuthService:
    def __init__(self, session: Session, user_repo: UsersRepository) -> None:
        self.session = session
        self.user_repo = user_repo

    def register_user(
        self,
        validated: UserRegister,
        role: UserRoleEnum = UserRoleEnum.USER,
    ) -> User:
        """Create user account.
        Must be pre-validated. Sets default userRole.USER
        """

        try:
            user = User(
                username=validated.username, name=validated.name, role=role, timezone=validated.timezone
            )
            user.hash_password(validated.password)
            self.session.add(user)
            # Also create UserProfile table w/ unit_system & h12 hour_cycle
            # TODO: find a better way to NOT make this assumption
            # Maybe get user locale from frontend somehow?
            # back_populates fills user_id at flush
            user.profile = UserProfile(unit_system=UnitSystemEnum.IMPERIAL, hour_cycle=HourCycleEnum.H12)
            user.goals = UserGoals()
            self.session.flush()
            seed_pillars(self.session, user.id) # seed core pillars
        except IntegrityError:
            raise ServiceError("Username already exists") from None
        return user

    def create_demo_user(self) -> User:
        username = f"demo_{secrets.token_hex(8)}"
        user = User(username=username, name="Guest", timezone="America/Chicago", role=UserRoleEnum.DEMO)
        user.set_unusable_password()
        user.profile = UserProfile(unit_system=UnitSystemEnum.IMPERIAL, hour_cycle=HourCycleEnum.H12)
        user.goals = UserGoals()
        self.session.add(user)
        self.session.flush()
        seed_pillars(self.session, user.id)
        seed_data(self.session, user.id)
        return user


def create_auth_service(session: Session, user_id: int) -> AuthService:
    return AuthService(
        session=session,
        # user_id=user_id,
        user_repo=UsersRepository(session),
        # pref_repo=UserPreferenceRepository(session, user_id),
    )
