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
def get_or_upsert_api_count(api_name, date, upsert=False):

    if upsert:
        # Postgres-specific, but one time won't hurt
        with database_connection() as session:
            session.execute(text("""
                INSERT INTO api_call_record (api_called, date, call_count)
                VALUES (:api_name, :date, 1)
                ON CONFLICT (api_called, date)
                DO UPDATE SET call_count = api_call_record.call_count + 1
                RETURNING call_count
        """), {"api_name": api_name, "date": date})
            
    else:
        with database_connection() as session:
            record = session.query(ApiCallRecord).filter(
                api_called=api_name,
                date=date
            ).first()
            current_app.logger.info(f"Record found: {record}")
            current_app.logger.info(f"Returning: {record.call_count if record else 0}")
            return record.call_count if record else 0

@api_bp.route('/weather/<city>/<units>')
def get_weather(city, units):
    today = datetime.now(timezone.utc).date()

    # Check current count
    current_count = get_or_upsert_api_count('openweathermap', today, upsert=False)

    
    current_app.logger.info(f"Current count: {current_count}")
    if current_count >= 700: # conservative
        return jsonify({"success": False, "message": "Error: Conservative usage limit reached/exceeded."})
    else:
        # Under limit -> Fulfill API request
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},uk&APPID={api_key}&units={units}"
        # 3.0: url = f"https://api.openweathermap.org/data/3.0/onecall/overview?lat={lat}&lon{lon}&APPID={api_key}&units={units}"
        response = requests.get(url)
        
        # Increment count
        get_or_upsert_api_count('openweathermap', today, upsert=True)

        return jsonify(response.json())