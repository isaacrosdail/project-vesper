# Currently just for OpenWeatherMap API calls

from flask import Blueprint, jsonify
import os
import requests
from datetime import datetime, timezone
from app.core.database import database_connection
from app.core.models import ApiCallRecord
from sqlalchemy import text

# debug
from flask import current_app

api_bp = Blueprint('api', __name__, url_prefix='/api')

# TODO: Review, practice patterns similar
def get_or_upsert_api_count(api_name, date, daily_limit, upsert=False):

    if upsert:
        # Postgres-specific, but one time won't hurt
        with database_connection() as session:
            # SQLAlchemy automatically converts our class name to a table name like below
            # ApiCallRecord (PascalCase) -> api_call_record (snake_case)
            result = session.execute(text("""
                INSERT INTO apicallrecord (api_called, date, call_count)
                VALUES (:api_name, :date, 1)
                ON CONFLICT (api_called, date)
                DO UPDATE SET call_count = apicallrecord.call_count + 1
                WHERE apicallrecord.call_count < :limit
                RETURNING call_count
        """), {"api_name": api_name, "date": date, "limit": daily_limit})
            return result.scalar_one_or_none() # TODO: NOTES: Add this & scalar_one()
            
    else:
        with database_connection() as session:
            record = session.query(ApiCallRecord).filter(
                ApiCallRecord.api_called==api_name,
                ApiCallRecord.date==date
            ).first()
            current_app.logger.info(f"Record found: {record}")
            current_app.logger.info(f"Returning: {record.call_count if record else 0}")
            return record.call_count if record else 0

def release_call(api_name, date):
    with database_connection() as session:
        session.execute(text(f"""
        UPDATE apicallrecord
        SET apicallrecord.call_count = GREATEST(apicallrecord.call_count - 1, 0)
        WHERE api_called = :a AND date = :d
    """), {"a": api_name, "d": date})

@api_bp.route('/weather/<city>/<units>')
def get_weather(city, units):
    today = datetime.now(timezone.utc).date()
    api_name = "openweathermap"
    DAILY_CALL_LIMIT = 700

    # Check current count
    current_count = get_or_upsert_api_count(api_name, today, DAILY_CALL_LIMIT, upsert=False)
    current_app.logger.info(f"Current count: {current_count}")

    # If over, error - else, call API
    if current_count >= DAILY_CALL_LIMIT: # conservative
        return jsonify({"success": False, "message": "Error: Conservative usage limit reached."}), 429 # Too many requests, rate limiting
    else:
        # Under limit -> Fulfill API request
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},uk&APPID={api_key}&units={units}"
        # 3.0: url = f"https://api.openweathermap.org/data/3.0/onecall/overview?lat={lat}&lon{lon}&APPID={api_key}&units={units}"
        
        # If successful call, increment count
        try:
            response = requests.get(url)        
            get_or_upsert_api_count(api_name, today, DAILY_CALL_LIMIT, upsert=True)
            return jsonify(response.json()), 200
        except:
            current_app.logger.exception("Upstream weather API failed.")
            release_call()
            return jsonify({"success": False, "error": "upstream_failed"})