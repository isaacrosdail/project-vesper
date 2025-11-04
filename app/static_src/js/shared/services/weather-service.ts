import { makeToast } from '../ui/toast.js';

export type WeatherResult = {
    temp: number | string;
    emoji: string;
    sunsetFormatted: string;
    sunrise: number | null;
    sunset: number | null;
}

export async function fetchWeatherData(): Promise<WeatherResult> {
    
    try {
        // TODO: Make flexible, based on userStore?
        const city = "Chicago";
        const country = "US";
        const units = "metric";

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

        const weatherConditions: Record<string, string> = {
            thunder: '⛈️',
            drizzle: '🌦️',
            rain: '🌧️',
            overcast: '☁️',
            snow: '❄️',
            mist: '🌫️',
            fog: '🌫️',
            clear: '☀️',
            "few clouds": '🌤️',
            scattered: '⛅',
            broken: '⛅',
            tornado: '🌪️'
        }
        // Find first weather condition key matching desc, return its emoji or undefined
        const emoji = Object.entries(weatherConditions).find(
            ([key]) => desc.includes(key)
        )?.[1] ?? '🌡️'; // "?? '🌡️'" <= Nullish coalescing: fallback if nothing found
        
        // Convert sunset time to date & local (TODO: Use helpers?)
        const sunsetTime = new Date(sunset * 1000); // Unix-style, so convert first
        const sunsetFormatted = sunsetTime.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });

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