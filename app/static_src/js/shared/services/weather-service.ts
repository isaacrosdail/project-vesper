import { makeToast } from '../ui/toast';
import { WeatherResult } from '../../types';
import { formatToUserTimeString } from '../datetime';

export async function fetchWeatherData(city: string, country: string, units: string): Promise<WeatherResult> {

    try {
        const response = await fetch(`/api/weather/${city}/${country}/${units}`);
        const weatherData = await response.json();

        if (!response.ok) {
            throw new Error(`Weather API failed: ${response.status}`);
        }

        // Process weatherData
        const temp = Math.round(weatherData.main.temp);
        const desc = weatherData.weather?.[0]?.description?.toLowerCase() ?? "";
        const sunrise = weatherData.sys.sunrise;
        const sunset = weatherData.sys.sunset;

        const weatherIcons: Record<string, string> = {
            thunder: 'icon-weather-thunder',
            drizzle: 'icon-weather-drizzle',
            rain: 'icon-weather-rain',
            overcast: 'icon-weather-clouds',
            snow: 'icon-weather-snow',
            mist: 'icon-weather-fog',
            fog: 'icon-weather-fog',
            clear: 'icon-weather-clear',
            "few clouds": 'icon-weather-clouds',
            scattered: 'icon-weather-clouds',
            broken: 'icon-weather-broken',
            tornado: 'icon-weather-tornado',
            "clear sky": 'icon-weather-clear'
        }
        const emoji = weatherIcons[desc] ?? '🌡️'; // TODO: fix, use svg instead or just nothing?
        
        // Convert sunset time to date & local (TODO: Use helpers?)
        const sunsetTime = new Date(sunset * 1000); // Unix-style, so convert first
        const sunsetFormatted = formatToUserTimeString(sunsetTime);

        return { temp, emoji, sunsetFormatted, sunrise, sunset };

    } catch (error) {
        console.error('Weather fetch failed:', error);
        makeToast('Issue fetching weather data', 'error', 2000);

        // Return fallbacks for UI
        return {
            temp: '--',
            emoji: '🌡️',
            sunsetFormatted: '--:--',
            sunrise: null,
            sunset: null
        }
    }
}