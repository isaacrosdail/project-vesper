from __future__ import annotations

import os
import secrets
from typing import TYPE_CHECKING

import requests

from app.modules.auth.schemas import (
    UserGoalsPatch,
    UserPatch,
    UserProfilePatch,
    UserRegister,
)

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


    # TODO: Fix this up
    def update_profile(self, patch: UserProfilePatch, user_id: int) -> User:
        # Now neeed to split: if modifying name or timezone -> UserPatch
        # if modifying city/units/etc -> UserProfilePatch
        user = self.user_repo.get_user_by_user_id(user_id)
        if not user:
            raise ServiceError("Issue finding user profile")
        data = patch.model_dump(exclude_unset=True)

        location_touched = {"city", "state", "country"} & data.keys()
        country = data.pop("country", user.profile.country)
        state = data.pop("state", None)
        city = data.pop("city", user.profile.city)

        # 1. State present, country != US -> 400
        if state and country != "US":
            raise ServiceError("State is only valid for US locations")
        # 2. City present, country missing OR city missing, country present:
        if (city is not None and country is None) or (city is None and country is not None):
            raise ServiceError("Both city and country required")

        for field, val in data.items():
            setattr(user.profile, field, val)

        # Geocode IF payload has city / state / country
        # Overrides above loop for country/city
        if location_touched:
            if city is None and country is None:
                return user
            result = self.geocode(city, state, country)
            # Store lat/lon
            user.profile.city = result["city"]
            # user.profile.state = state
            user.profile.country = result["country"]
            user.profile.latitude = result["lat"]
            user.profile.longitude = result["lon"]

        return user

    def update_user(self, patch: UserPatch, user_id: int) -> User:
        user = self.user_repo.get_user_by_user_id(user_id)
        if not user:
            raise ServiceError("User not found")
        data = patch.model_dump(exclude_unset=True)
        for field, val in data.items():
            setattr(user, field, val)
        return user

    def update_goals(self, patch: UserGoalsPatch, user_id: int) -> User:
        user = self.user_repo.get_user_by_user_id(user_id)
        if not user:
            raise ServiceError("User not found")
        data = patch.model_dump(exclude_unset=True)
        for field, val in data.items():
            setattr(user.goals, field, val)
        return user

    # draft geocode:
    def geocode(self, city: str, state: str | None, country: str) -> dict[str, str | float]:
        # with city and country -> get lat/lon if we don't have it already
        query = f"{city},{state},{country}" if state else f"{city},{country}"
        API_KEY = os.environ.get("OPENWEATHER_API_KEY")
        GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
        # url = "someurl"
        # api_key = "123324"
        try:
            resp = requests.get(GEOCODE_URL, params={"q": query, "limit": 1, "appid": API_KEY}, timeout=5)
            resp.raise_for_status()
            results = resp.json()
        except requests.RequestException:
            raise ServiceError("Location service unavailable", status_code=502) from None
        if not results:
            raise ServiceError("Could not resolve that location")
        return {
            "city": results[0]["name"],
            "country": results[0]["country"],
            "lat": results[0]["lat"],
            "lon": results[0]["lon"]
        }


def create_auth_service(session: Session, user_id: int) -> AuthService:
    return AuthService(
        session=session,
        # user_id=user_id,
        user_repo=UsersRepository(session),
        # pref_repo=UserPreferenceRepository(session, user_id),
    )


