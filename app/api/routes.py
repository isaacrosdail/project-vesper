"""API routes for:
- /profile/me: User profile data for frotend (userStore)
- /weather: External OpenWeatherMap integration (rate-limited)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import logging
import os
from datetime import datetime, timezone

import requests
from flask import Response, current_app, jsonify
from flask_login import current_user

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.rate_limiter import release_slot, reserve_slot
from app.api.responses import api_response
from app.modules.auth.service import typed_login_required

logger = logging.getLogger(__name__)


@api_bp.get("/profile/me")
@typed_login_required
def get_my_profile() -> Response:
    """Internal API for fetching profile information used in JS."""
    return jsonify(
        {
            "timezone": current_user.timezone,
            "units": current_user.units.value,
            "city": current_user.city,
            "country": current_user.country,
        }
    )


@api_bp.get("/weather/<city>/<country>/<units>")
@with_db_session
def get_weather(
    session: Session, city: str, country: str, units: str
) -> tuple[Response, int]:
    """Fetch current weather data from OpenWeatherMap for a given city and country,
    with rate limiting enforced per API key.
    """
    today = datetime.now(timezone.utc).date()
    api_name = "openweathermap"
    DAILY_CALL_LIMIT = current_app.config.get("OPENWEATHER_DAILY_LIMIT", 700)

    if not city or not country:
        return api_response(success=False, message="Missing city/country"), 400

    VALID_UNITS = {
        "metric",
        "imperial",
        "standard",
    }  # OpenWeatherMap defaults to standard, so we'll default to metric instead
    units = units if units in VALID_UNITS else "metric"

    reserved_count = reserve_slot(session, api_name, today, DAILY_CALL_LIMIT)
    logger.info("Reserved count after upsert: %s", reserved_count)
    if reserved_count is None:
        return api_response(success=False, message="Error: Usage limit reached"), 429

    api_key = os.environ.get("OPENWEATHER_API_KEY")

    url = "https://api.openweathermap.org/data/2.5/weather?"
    params = {
        "q": f"{city},{country}",
        "APPID": api_key,
        "units": units,
    }

    def fail(code: int, message: str) -> tuple[Response, int]:
        release_slot(session, api_name, today)
        return api_response(success=False, message=message), code

    # Call API, release slot on failure
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # raises on 4xx/5xx
    except requests.Timeout:
        logger.exception("Upstream weather API timeout.")
        return fail(504, "upstream_timeout")

    except requests.HTTPError as e:
        status_code = e.response.status_code

        if 400 <= status_code < 500:  # noqa: PLR2004 'magic number'
            # Client-side error: bad city/country, API key, etc?
            return fail(400, f"Invalid request: {e.response.text}")
        return fail(503, "Weather service unavailable")

    except requests.RequestException:
        # Network-level failure (DNS, conn refused, etc.)
        logger.exception("Upstream weather API failed.")
        return fail(502, "upstream_failed")

    else:
        return jsonify(response.json()), 200
