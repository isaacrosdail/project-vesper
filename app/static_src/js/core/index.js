import { formatTimeString } from '../shared/datetime.js';
import { getJSInstant } from '../shared/datetime.js';
import { fetchWeatherData } from '../shared/services/weather-service.js';
import { calcCelestialBodyPos, CelestialRenderer, setupCanvas } from '../shared/canvas.js';
import { makeToast } from '../shared/ui/toast.js';

// Global caches
let weatherInfo = null;  // for weatherInfo
// let cachedSunPos = null; // for sunPos
// let currentBodyType = 'moon';
let currentCanvasState = null;
let resizeTimeout = null;
let renderer;

/**
 * Marks a habit as complete/incomplete & updates the UI accordingly.
 * @async
 * @param {HTMLInputElement} checkbox - The checkbox that was clicked 
 * @param {number} habitId - The ID of the habit to update
 * @returns {Promise<void>} 
 */
async function markHabitComplete(checkbox, habitId) {
    try {
        // Mark complete => POST HabitCompletion
        // Get instant user clicks "done"
        const completedAtUTC = getJSInstant();
        if (checkbox.checked) {
            const response = await fetch(`/habits/${habitId}/completions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({completed_at: completedAtUTC}) // send JSON string
            });
            const responseData = await response.json(); // convert json to obj

            if (responseData.success) {
                const row = checkbox.closest('.habit-row'); // scope query to right <label> row
                const emojiSpan = row.querySelector('.habit-streak');
                const listItem = row.closest('.habit-item'); // grab <li>

                let streakCount = parseInt(emojiSpan.dataset.streakCount, 10);
                streakCount += 1;
                emojiSpan.dataset.streakCount = streakCount;

                listItem?.classList.toggle('completed');
                emojiSpan.textContent = `🔥${streakCount}`;
            } else {
                console.error('Error marking habit complete:', responseData.message);
            }
        } else {
            // TODO: NOTES: Built this to accept any date via query parameter (the "?=.." thing) for future flexibility
            // but currently we only ever delete today's completion from our main dashboard
            // So the route CAN handle any date, but our JS will stick to today
            //const todayDateOnly = new Date().toISOString().split('T')[0]; // Gives format like "2025-06-26"
            const todayDateOnly = new Intl.DateTimeFormat('en-CA').format(new Date());
            const response = await fetch(`/habits/${habitId}/completion?date=${todayDateOnly}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
            });
            const responseData = await response.json(); // Wait for JSON parsing

            if (responseData.success) {
                // un-apply effect/styling (update DOM)
                const row = checkbox.closest('.habit-row');
                const emojiSpan = row.querySelector('.habit-streak');
                const listItem = row.closest('.habit-item');

                let streakCount = parseInt(emojiSpan.dataset.streakCount, 10);
                streakCount -= 1;
                emojiSpan.dataset.streakCount = streakCount;

                listItem?.classList.toggle('completed');
                if (streakCount > 0) {
                    emojiSpan.textContent = `🔥${streakCount}`;
                } else {
                    emojiSpan.textContent = "";
                }
            } else {
                console.error('Error un-marking habit complete:', responseData.message);
            }
        }
    } catch (error) {
        console.error('Error during habit completion request:', error);
    }
}

function updateClock() {
    const timeDisplay = document.querySelector('#time-display');
    timeDisplay.textContent = formatTimeString();
}

// Get weather info via API, orchestrates our sun movement
// TODO: Un-hardcode city + units (get from userStore in fetchWeatherData itself?)
async function getWeatherInfo() {
    const tempDisplay = document.querySelector('#weather-temp');
    const sunsetDisplay = document.querySelector('#weather-sunset');
    const city = "London";
    const units = "metric";

    tempDisplay.textContent = "Loading weather info...";
    weatherInfo = await fetchWeatherData();

    // Display temp with units & formatted sunset time
    // Destructure what we need
    const { temp, emoji, sunsetFormatted } = weatherInfo;
    tempDisplay.textContent = `${temp}°${units === 'metric' ? 'C' : 'F'} ${emoji}`;
    sunsetDisplay.textContent = `Sunset: ${sunsetFormatted} 🌅`;
}

function updateCelestialBodyPos() {
    if (!weatherInfo) return;

    const now = Math.floor(Date.now() / 1000); // convert to seconds to compare to what API gave
    const { sunrise, sunset } = weatherInfo;
    let position;
    let bodyType = 'moon';

    if (now >= sunrise && now <= sunset) {
        // Daytime
        bodyType = 'sun';
        position = calcCelestialBodyPos(sunrise, sunset, now);
    } else if (now > sunset) {
        // Tonight (after sunset)
        const nextSunrise = sunrise + (24 * 60 * 60);
        position = calcCelestialBodyPos(sunset, nextSunrise, now); // Just flip to find progress between sunset and tomorrow's sunrise, close enough for a widget!
    } else {
        // Last night (before sunrise)
        const prevSunset = sunset - (24 * 60 * 60);
        position = calcCelestialBodyPos(prevSunset, sunrise, now);
    }

    currentCanvasState = {
        bodyType: bodyType,
        x: position.x,
        y: position.y
    };

    redrawCanvas();
}

/**
 * Trigger canvas redraw upon resizing
 */
function redrawCanvas() {
    setupCanvas();
    if (currentCanvasState) {
        //drawCelestialBody(currentCanvasState.x, currentCanvasState.y, currentCanvasState.bodyType);
        renderer.draw(
            currentCanvasState.x, 
            currentCanvasState.y, 
            currentCanvasState.bodyType
        );
    }
}

export function init() {
    const hasWeatherSection = document.querySelector('.weather-section');
    const hasHabits = document.querySelector('.habit-checkbox');
    if (!hasWeatherSection && !hasHabits) return;

    document.addEventListener('change', (e) => {
        if (e.target.matches('.habit-checkbox')) {
            markHabitComplete(e.target, e.target.dataset.habitId);
        }
    });

    // Weather setup
    if (hasWeatherSection) {
        renderer = new CelestialRenderer('#sky-canvas');
        getWeatherInfo();         // Cache weather data
        updateCelestialBodyPos(); // Draw sun immediately
        setInterval(getWeatherInfo, 1*60*60*1000);  // Update weather every hour
        setInterval(updateCelestialBodyPos, 6000); // Update sun from weatherInfo every 10 mins => 10*60*1000
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(redrawCanvas, 100); // debounce redraw
        });
    }
    // Clock setup
    if (document.querySelector('#time-display')) {
        setInterval(updateClock, 30 * 1000);
        updateClock();
    }
}