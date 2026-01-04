"""
API routes for:
- /profile/me: User profile data for frotend (userStore)
- /weather: External OpenWeatherMap integration (rate-limited)
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import os

from datetime import datetime, timezone

import requests
from flask import current_app, jsonify, Response
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.responses import api_response
from app.api.rate_limiter import release_slot, reserve_slot

import logging
logger = logging.getLogger(__name__)


@api_bp.get('/profile/me')
@login_required # type: ignore
def get_my_profile() -> Response:
    """Internal API for fetching profile information used in JS."""
    return jsonify({
        'timezone': current_user.timezone,
        'units': current_user.units.value,
        'city': current_user.city,
        'country': current_user.country
    })


@api_bp.get('/weather/<city>/<country>/<units>')
@with_db_session
def get_weather(session: 'Session', city: str, country: str, units: str) -> tuple[Response, int]:
    """
    Fetch current weather data from OpenWeatherMap for a given city and country,
    with rate limiting enforced per API key.
    """
    today = datetime.now(timezone.utc).date()
    api_name = "openweathermap"
    DAILY_CALL_LIMIT = current_app.config.get("OPENWEATHER_DAILY_LIMIT", 700)

    if not city or not country:
        return api_response(False, "Missing city/country"), 400
    
    VALID_UNITS = {"metric", "imperial", "standard"} # OpenWeatherMap defaults to standard, so we'll default to metric instead
    units = units if units in VALID_UNITS else "metric"

    reserved_count = reserve_slot(session, api_name, today, DAILY_CALL_LIMIT)
    logger.info(f"Reserved count after upsert: {reserved_count}")
    if reserved_count is None:
        return api_response(False, "Error: Usage limit reached"), 429
    
    api_key = os.environ.get('OPENWEATHER_API_KEY')

    url = "https://api.openweathermap.org/data/2.5/weather?"
    params = {
        "q": f"{city},{country}",
        "APPID": api_key,
        "units": units,
    }

    # Call API, release slot on failure
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # raises on 4xx/5xx
    except requests.Timeout:
        logger.exception("Upstream weather API timeout.")
        release_slot(session, api_name, today)
        return api_response(False, "upstream_timeout"), 504
    except requests.RequestException:
        logger.exception("Upstream weather API failed.")
        release_slot(session, api_name, today)
        return api_response(False, "upstream_failed"), 502
    else:
        return jsonify(response.json()), 200