# Currently just for OpenWeatherMap API calls

import os
from datetime import datetime, timezone

import requests
from flask import Blueprint, current_app, jsonify
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.api.service import release_slot, reserve_slot

api_bp = Blueprint('api', __name__, url_prefix='/api', template_folder='templates')


"""Internal API endpoints to feed JS frontend / facilitate PATCH/DELETEs."""
@api_bp.route('/profile/me')
@login_required
def get_my_profile():
    """Internal API for fetching profile information used in JS."""
    return jsonify({
        'timezone': current_user.timezone
    })

# Draft API endpoint for D3-based visualizations.
@api_bp.route('/my-graph')
@login_required
def my_graph_data():
    data = [
        {"day": "Mon", "value": 11 },
        {"day": "Tue", "value": 13 },
        {"day": "Wed", "value": 7 }
    ]
    return data

"""External API endpoints to call or return data to third-party services. For fetching weather data as well as for our health check."""
@api_bp.route('/weather/<city>/<units>')
@with_db_session
def get_weather(session, city, units):
    """External API call-limiting function to ensure we exceed limits."""
    today = datetime.now(timezone.utc).date()
    api_name = "openweathermap"
    DAILY_CALL_LIMIT = current_app.config.get("OPENWEATHER_DAILY_LIMIT", 700)
    country = current_app.config.get("OPENWEATHER_COUNTRY", "uk") # TODO: Change default

    # Reserve a slot atomically
    reserved_count = reserve_slot(session, api_name, today, DAILY_CALL_LIMIT)
    current_app.logger.info(f"Reserved count after upsert: {reserved_count}")
    if reserved_count is None:
        return jsonify({
            "success": False,
            "message": "Error: Conservative usage limit reached."
        }), 429 # Too many requests, rate limiting
    
    # Build request
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    # TODO: Pick one & make query params adaptable
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&APPID={api_key}&units={units}"
    # 3.0: url = f"https://api.openweathermap.org/data/3.0/onecall/overview?lat={lat}&lon{lon}&APPID={api_key}&units={units}"
    
    # Call API, release slot on failure
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # raises on 4xx/5xx
    except requests.Timeout:
        current_app.logger.exception("Upstream weather API timeout.")
        release_slot(api_name, today)
        return jsonify({"success": False, "message": "upstream_timeout"}), 504
    except requests.RequestException:
        current_app.logger.exception("Upstream weather API failed.")
        release_slot(session, api_name, today)
        return jsonify({"success": False, "message": "upstream_failed"}), 502
    else:
        return jsonify(response.json()), 200