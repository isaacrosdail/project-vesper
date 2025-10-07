# Currently just for OpenWeatherMap API calls

import os
from datetime import datetime, timezone

import requests
from flask import Blueprint, current_app, jsonify
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.api import api_bp
from app.api.responses import api_response
from app.api.service import release_slot, reserve_slot


"""Internal API endpoints to feed JS frontend / facilitate PATCH/DELETEs."""
@api_bp.route('/profile/me')
@login_required
def get_my_profile():
    """Internal API for fetching profile information used in JS."""
    return jsonify({
        'timezone': current_user.timezone
    })


"""External API endpoints to call or return data to third-party services. For fetching weather data as well as for our health check."""
@api_bp.route('/weather/<city>/<country>/<units>')
@with_db_session
def get_weather(session, city, country, units):
    """External API call-limiting function to ensure we exceed limits."""
    today = datetime.now(timezone.utc).date()
    api_name = "openweathermap"
    DAILY_CALL_LIMIT = current_app.config.get("OPENWEATHER_DAILY_LIMIT", 700)
    # country = current_app.config.get("OPENWEATHER_COUNTRY", "uk") # TODO: Change default
    country = country or "uk"

    # Reserve a slot atomically
    reserved_count = reserve_slot(session, api_name, today, DAILY_CALL_LIMIT)
    current_app.logger.info(f"Reserved count after upsert: {reserved_count}")
    if reserved_count is None:
        return api_response(False, "Error: Conservative usage limit reached"), 429 # Too many requests/rate limiting
    
    # Build request
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&APPID={api_key}&units={units}"
    
    # Call API, release slot on failure
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # raises on 4xx/5xx
    except requests.Timeout:
        current_app.logger.exception("Upstream weather API timeout.")
        release_slot(api_name, today)
        return api_response(False, "upstream_timeout"), 504
    except requests.RequestException:
        current_app.logger.exception("Upstream weather API failed.")
        release_slot(session, api_name, today)
        return api_response(False, "upstream_failed"), 502
    else:
        return jsonify(response.json()), 200