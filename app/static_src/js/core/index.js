import { formatTimeString } from '../shared/datetime.js';
import { getJSInstant } from '../shared/datetime.js';
import { fetchWeatherData } from '../shared/services/weather-service.js';
import { calcCelestialBodyPos, CelestialRenderer, setupCanvas } from '../shared/canvas.js';
import { makeToast } from '../shared/ui/toast.js';
import { apiRequest } from '../shared/services/api.js';

// Global caches
let weatherInfo = null;
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
        const completedAtUTC = getJSInstant();  // Get instant user clicks "done"
        if (checkbox.checked) {
            const url = `/habits/${habitId}/completions`;
            const data = { completed_at: completedAtUTC };

            apiRequest('POST', url, () => {
                const row = checkbox.closest('.item-row'); // scope query to right <label> row
                const emojiSpan = row.querySelector('.habit-streak');
                const listItem = row.closest('.item'); // grab <li>

                let streakCount = parseInt(emojiSpan.dataset.streakCount, 10);
                streakCount += 1;
                emojiSpan.dataset.streakCount = streakCount;

                listItem?.classList.toggle('completed');
                emojiSpan.textContent = `🔥${streakCount}`;
            }, data);
        } else {
            const todayDateOnly = new Intl.DateTimeFormat('en-CA').format(new Date());
            const url = `/habits/${habitId}/completion?date=${todayDateOnly}`;

            apiRequest('DELETE', url, () => {
                // un-apply effect/styling (update DOM)
                const row = checkbox.closest('.item-row');
                const emojiSpan = row.querySelector('.habit-streak');
                const listItem = row.closest('.item');

                let streakCount = parseInt(emojiSpan.dataset.streakCount, 10);
                streakCount -= 1;
                emojiSpan.dataset.streakCount = streakCount;

                listItem?.classList.toggle('completed');
                if (streakCount > 0) {
                    emojiSpan.textContent = `🔥${streakCount}`;
                } else {
                    emojiSpan.textContent = "";
                }
            });
        }
    } catch (error) {
        console.error('Error during habit completion request:', error);
    }
}
async function markTaskComplete(checkbox, taskId) {
    const completedAtUTC = getJSInstant();
    const url = `/tasks/task/${taskId}`;

    let data;
    if (checkbox.checked) {
        data = {
            is_done: true,
            completed_at: completedAtUTC 
        };
    } else {
        data = {
            is_done: false,
            completed_at: null
        }
    }
    console.log(data)
    apiRequest('PATCH', url, () => {
        const listItem = checkbox.closest('.item');
        listItem?.classList.toggle('completed');
    }, data);

}

async function markTaskComplete(checkbox, taskId) {
    const completedAtUTC = getJSInstant();
    const url = `/tasks/task/${taskId}`;

    let data;
    if (checkbox.checked) {
        data = {
            is_done: true,
            completed_at: completedAtUTC 
        };
    } else {
        data = {
            is_done: false,
            completed_at: null
        }
    }
    apiRequest('PATCH', url, () => {
        const listItem = checkbox.closest('.item');
        listItem?.classList.toggle('completed');
    }, data);

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
        if (e.target.matches('.task-checkbox')) {
            markTaskComplete(e.target, e.target.dataset.taskId);
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