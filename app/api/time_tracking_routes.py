
from flask import request, current_app
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.service import TimeTrackingService
from app.modules.time_tracking.validators import validate_time_entry
from app.shared.parsers import parse_time_entry_form_data


@api_bp.route('/time_tracking/time_entries', methods=["POST"])
@api_bp.route('/time_tracking/time_entries/<int:entry_id>', methods=["PUT"])
@login_required
@with_db_session
def time_entries(session, entry_id=None):
        parsed_data = parse_time_entry_form_data(request.form.to_dict())

        typed_data, errors = validate_time_entry(parsed_data)
        if errors:
            current_app.logger.info(f"Validation errors: {errors}")
            return validation_failed(errors), 400

        repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
        service = TimeTrackingService(repo, current_user.timezone)
        result = service.save_time_entry(typed_data, entry_id)

        if not result["success"]:
            return api_response(False, result["message"], errors=result["errors"])

        entry = result["data"]["entry"]
        return api_response(
            True,
            result["message"],
            data = entry.to_api_dict()
        ), 201