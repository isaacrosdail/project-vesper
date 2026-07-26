"""API routes for:
- /profile/me: User profile data for frotend (userState)
- /weather: External OpenWeatherMap integration (rate-limited)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.api.responses import success_response
from app.errors import ErrorResponse, error_response

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import logging
import os
from datetime import datetime, timezone

import requests
from flask import Response, current_app, jsonify, request
from flask_login import current_user

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.rate_limiter import release_slot, reserve_slot
# from app.modules.auth.repository import UserPreferenceRepository
from app.modules.auth.service import create_auth_service
from app.shared.decorators import login_plus_session

logger = logging.getLogger(__name__)


@api_bp.get("/weather/<city>/<country>/<units>")
@with_db_session
def get_weather(
    session: Session, city: str, country: str, units: str
) -> tuple[Response | ErrorResponse, int]:
    """Fetch current weather data from OpenWeatherMap for a given city and country,
    with rate limiting enforced per API key.
    """
    today = datetime.now(timezone.utc).date()
    api_name = "openweathermap"
    DAILY_CALL_LIMIT = current_app.config.get("OPENWEATHER_DAILY_LIMIT", 700)

    if not city or not country:
        return error_response(message="Missing city/country", status_code=400, code="MISSING CITY/COUNTRY")

    VALID_UNITS = {
        "metric",
        "imperial",
        "standard",
    }  # OpenWeatherMap defaults to standard, so we'll default to metric instead
    units = units if units in VALID_UNITS else "metric"

    reserved_count = reserve_slot(session, api_name, today, DAILY_CALL_LIMIT)
    logger.info("Reserved count after upsert: %s", reserved_count)
    if reserved_count is None:
        return error_response(message="Error: Usage limit reached", status_code=429, code="RATE_LIMITED")

    api_key = os.environ.get("OPENWEATHER_API_KEY")

    url = "https://api.openweathermap.org/data/2.5/weather?"
    params = {
        "q": f"{city},{country}",
        "APPID": api_key,
        "units": units,
    }

    def fail(status_code: int, code: str, message: str) -> tuple[ErrorResponse, int]:
        release_slot(session, api_name, today)
        return error_response(message=message, status_code=status_code, code=code)

    # Call API, release slot on failure
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # raises on 4xx/5xx
    except requests.Timeout:
        logger.exception("Upstream weather API timeout.")
        return fail(504, "UPSTREAM_TIMEOUT", "Weather service timed out")

    except requests.HTTPError as e:
        status_code = e.response.status_code

        if 400 <= status_code < 500:  # noqa: PLR2004 'magic number'
            # Client-side error: bad city/country, API key, etc?
            return fail(400, "UPSTREAM_REJECTED", "Weather service rejected the request")
        return fail(503, "UPSTREAM_UNAVAILABLE", "Weather service unavailable")

    except requests.RequestException:
        # Network-level failure (DNS, conn refused, etc.)
        logger.exception("Upstream weather API failed.")
        return fail(502, "UPSTREAM_FAILED", "Couldn't reach weather service")

    else:
        return success_response(message="Weather data received", data=response.json()), 200

