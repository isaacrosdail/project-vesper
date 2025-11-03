import sys
from zoneinfo import ZoneInfo
from flask import request, current_app
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.metrics.repository import DailyMetricsRepository, ABTestRepository, ABTrialRepository
from app.modules.metrics.service import DailyMetricsService
from app.modules.metrics.validators import validate_daily_entry
from app.shared.parsers import parse_daily_entry_form_data, parse_abtest_form_data, parse_abtrial_form_data
from app.shared.datetime.helpers import last_n_days_range


@api_bp.route("/metrics/daily_entries", methods=["POST"])
@api_bp.route("/metrics/daily_entries/<int:entry_id>", methods=["PUT"])
@login_required
@with_db_session
def daily_entries(session, entry_id=None):

    parsed_data = parse_daily_entry_form_data(request.form.to_dict())
    typed_data, errors = validate_daily_entry(parsed_data)

    if errors:
        return validation_failed(errors), 400
    
    repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
    service = DailyMetricsService(repo, current_user.timezone)
    result = service.save_daily_entry(typed_data, entry_id)

    if not result["success"]:
        return api_response(False, result["message"], errors=result["errors"])

    entry = result["data"]["entry"]
    return api_response(
        True,
        result["message"],
        data = entry.to_api_dict()
    ), 201

@api_bp.route("/metrics/ab_tests", methods=["POST"])
@login_required
@with_db_session
def ab_tests(session):
    parsed_data = parse_abtest_form_data(request.form.to_dict())
    # logger.debug(f"[ABTests] Parsed form data: {parsed_data}")
    # current_app.logger.info(f"Parsed form data: {parsed_data}\n")
    # skip validation for now
    repo = ABTestRepository(session, current_user.id, current_user.timezone)
    result = repo.create_abtest(**parsed_data)

    return api_response(
        True,
        "Saved abtest",
        data=result.to_api_dict()
    ), 201

@api_bp.route("/metrics/ab_trials", methods=["POST"])
@login_required
@with_db_session
def ab_trials(session):
    parsed_data = parse_abtrial_form_data(request.form.to_dict())
    # logger.info(f"Parsed form data: {parsed_data}\n")
    # skip validation
    repo = ABTrialRepository(session, current_user.id, current_user.timezone)
    result = repo.create_abtrial(**parsed_data)

    return api_response(
        True,
        "Saved abtrial",
        data=result.to_api_dict()
    ), 201

@api_bp.get("/metrics/daily_entries/linechart")
@login_required
@with_db_session
def linechart(session):
    type = request.args.get("type")
    lastNDays = int(request.args.get("lastNDays"))

    repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = last_n_days_range(lastNDays, repo.user_tz)
    results = repo.get_metrics_by_type_in_window(type, start_utc, end_utc)

    logger.debug(f"result: {results}")
    return api_response(
        True,
        "Great success",
        data = [
            {"date": dt.astimezone(ZoneInfo(current_user.timezone)).isoformat(), "value": value}
            for dt, value in results
        ]
    )