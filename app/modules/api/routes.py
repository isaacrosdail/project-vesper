# Currently just for OpenWeatherMap API calls

import os
from datetime import datetime, timezone

import requests
from app.modules.api.service import release_slot, reserve_slot
from flask import Blueprint, current_app, jsonify

api_bp = Blueprint('api', __name__, url_prefix='/api', template_folder='templates')

# TODO: NOTES: ApiCallRecord (PascalCase) -> api_call_record (snake_case)
# SQLAlchemy automatically converts our class name to a table name like below
# ... ON CONFLICT ... WHERE call_count < :limit    <= atomic

@api_bp.route('/weather/<city>/<units>')
def get_weather(city, units):
    today = datetime.now(timezone.utc).date()
    api_name = "openweathermap"
    DAILY_CALL_LIMIT = current_app.config.get("OPENWEATHER_DAILY_LIMIT", 700)
    country = current_app.config.get("OPENWEATHER_COUNTRY", "uk") # TODO: Change default

    # Reserve a slot atomically
    reserved_count = reserve_slot(api_name, today, DAILY_CALL_LIMIT)
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
    except requests.RequestException:
        current_app.logger.exception("Upstream weather API timeout.")
        release_slot(api_name, today)
        return jsonify({"success": False, "message": "upstream_timeout"}), 504
    except requests.Timeout:
        current_app.logger.exception("Upstream weather API failed.")
        release_slot(api_name, today)
        return jsonify({"success": False, "message": "upstream_failed"}), 502
    else:
        return jsonify(response.json()), 200