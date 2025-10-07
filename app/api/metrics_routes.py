
from flask import request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.metrics.repository import DailyMetricsRepository
from app.modules.metrics.service import DailyMetricsService
from app.modules.metrics.validators import validate_daily_entry
from app.shared.parsers import parse_daily_entry_form_data


@api_bp.route("/metrics/entries", methods=["POST"])
@login_required
@with_db_session
def metrics(session):

    parsed_data = parse_daily_entry_form_data(request.form.to_dict())
    typed_data, errors = validate_daily_entry(parsed_data)

    if errors:
        return validation_failed(errors), 400
    
    repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
    service = DailyMetricsService(repo, current_user.timezone)
    result = service.process_daily_metrics(typed_data)

    if not result["success"]:
        return api_response(False, result["message"], errors=result["errors"])

    return api_response(
        True,
        result["message"],
        data = result["data"] # pass through the data dict
    ), 201