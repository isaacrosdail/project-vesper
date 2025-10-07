
from flask import request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.service import TimeTrackingService
from app.modules.time_tracking.validators import validate_time_entry
from app.shared.parsers import parse_time_entry_form_data


@api_bp.route('/time_tracking/entries', methods=["POST"])
@login_required
@with_db_session
def time_entries(session):
        parsed_data = parse_time_entry_form_data(request.form.to_dict())

        typed_data, errors = validate_time_entry(parsed_data)
        if errors:
            return validation_failed(errors), 400

        repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
        service = TimeTrackingService(repo, current_user.timezone)
        result = service.create_entry_from_form(typed_data)

        if not result["success"]:
            return api_response(False, result["message"], errors=result["errors"])

        entry = result["data"]["entry"]
        return api_response(
            True,
            result["message"],
            data = {
                "id": entry.id,
                "category": entry.category,
                "duration": entry.duration_minutes,
                "started_at": entry.started_at.isoformat(),
                "description": entry.description
            }
        ), 201