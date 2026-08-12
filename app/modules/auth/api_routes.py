from __future__ import annotations

from typing import TYPE_CHECKING

from app.api import api_bp
from app.api.responses import success_response
from app.modules.auth.schemas import UserGoalsPatch, UserGoalsRead, UserPatch, UserProfilePatch, UserProfileRead
from app.shared.repository.pillar import PillarRepository
from app.shared.schemas import PillarRead

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Response, jsonify, request
from flask_login import current_user

from app.modules.auth.service import create_auth_service
from app.shared.decorators import login_plus_session


@api_bp.get("/profile/me")
@login_plus_session
def get_my_profile(session: Session) -> tuple[Response, int]:
    """Internal API for fetching profile information used in JS."""
    return success_response(
        message="Profile retrieved",
        data={
            "is_owner": current_user.is_owner,
            "timezone": current_user.timezone,
            "profile": UserProfileRead.dump(current_user.profile),
            "goals": UserGoalsRead.dump(current_user.goals),
        }), 200

@api_bp.patch("/users/me")
@login_plus_session
def update_user(session: Session) -> tuple[Response, int]:
    validated = UserPatch(**request.json)
    auth_service = create_auth_service(session, current_user.id)
    auth_service.update_user(validated, current_user.id)
    return success_response(message="User updated"), 200

@api_bp.patch("/profile/me")
@login_plus_session
def update_profile(session: Session) -> tuple[Response, int]:
    validated = UserProfilePatch(**request.json)
    auth_service = create_auth_service(session, current_user.id)
    auth_service.update_profile(validated, current_user.id)
    return success_response(message="User profile updated"), 200

@api_bp.patch("/goals/me")
@login_plus_session
def update_goals(session: Session) -> tuple[Response, int]:
    validated = UserGoalsPatch(**request.json)
    auth_service = create_auth_service(session, current_user.id)
    auth_service.update_goals(validated, current_user.id)
    return success_response(message="User goals updated"), 200


## TODO(api): Putting this here for now since it IS account-wide.
@api_bp.get("/pillars")
@login_plus_session
def get_pillars(session: Session) -> tuple[Response, int]:
    pillar_repo = PillarRepository(session, current_user.id)
    pillars = pillar_repo.get_all()

    return success_response(message="Pillars retrieved", data=[PillarRead.dump(p) for p in pillars]), 200
