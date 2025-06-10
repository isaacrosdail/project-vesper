# Currently just for OpenWeatherMap API calls

from flask import Blueprint, jsonify
import os
import requests

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/weather/<city>/<units>')
def get_weather(city, units):
    # get key
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    # build openweather url
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},uk&APPID={api_key}&units={units}"
    response = requests.get(url)
    
    return jsonify(response.json())