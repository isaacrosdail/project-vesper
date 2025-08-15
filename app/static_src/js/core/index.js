import { formatDateString } from '../shared/datetime.js';
import { getJSInstant } from '../shared/datetime.js';
import { userStore } from '../shared/userStore.js';

// Global caches
let weatherInfo = null;  // for weatherInfo
let cachedSunPos = null; // for sunPos (for redrawing after Canvas resizing)

/**
 * Function for inputting time entries via our activity log card inputs
 * @param {HTMLElement} element - The "Save Entry" button in our activity log card
 */
async function saveTimeEntry(element) {
    // Grabbing our elements from there
    const card = element.closest('#activity-log-card');
    const categoryElement = card.querySelector('[name="category"]');
    const durationElement = card.querySelector('[name="duration"]');
    const descriptionElement = card.querySelector('[name="description"]');

    // Getting values for POST
    const category = categoryElement.value;
    const duration = durationElement.value;
    const description = descriptionElement.value;

    try {
        // Now our async fetch
        const response = await fetch('/time_tracking/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category: category,
                duration: duration,
                description: description
            })
        });
        const responseData = await response.json();

        if (responseData.success) {
            // Clear our inputs
            categoryElement.value = '';
            durationElement.value = '';
            descriptionElement.value = '';
        } else {
            console.error('Error saving entry: ', responseData.message);
        }
    }
    catch (error) {
        console.error('Failed to save/update: ', error);
    }
}


// Handle UI (span -> input field)
// TODO: Condense into general inlineEdit (w/ editTableField func)
/**
 * Converts a span element into an input field for inline editing
 * @param {HTMLElement} element - The span element containing text to edit
 * @description
 * - Replaces span content with size-appropriate input field pre-populated with original text
 * - Save changes on blur/enter (if not empty) or reverts to original text
 */
function editIntention(element) {
    const originalText = element.textContent.trim();

    // TODO: innerHTML here presents XSS risk?
    // Replace innerHTML of span with input field & pre-populate with current text
    element.innerHTML = `<input type="text" value="${originalText}" size="${originalText.length + 2}">`;
    // Grab the input element inside our span element & focus it
    const input = element.querySelector('input');
    input.focus();

    // Now set up event listeners for our blur event (to save => call updateIntention)
    input.addEventListener('blur', function() {
        if (input.value.trim() !== '') {
            updateIntention(element, input.value); // pass our new text
        } else {
            element.innerHTML = originalText; // Don't save if input is left empty
        }
    });
    // Trigger blur on enter key
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            input.blur();
        }
    });
}


async function updateIntention(element, newValue) {
    try {
        const response = await fetch('/daily-intentions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ intention: newValue })
        });

        const responseData = await response.json();

        if (responseData.success) {
            element.innerHTML = `${newValue}`; // replace input field with just newValue text upon success
        } else {
            // Handle the Flask route error
            console.error('Error saving intention:', responseData.message);
        }
    
    } catch (error) {
        console.error('Failed to save/update:', error);
    }
}

/**
 * Saves input data based on input's data attributes (metric or checkin)
 * @param {HTMLElement} input - Input element containing data to save
 * @description
 * - Only saves if input has a value (allows partial form completion)
 */
async function saveData(input) {
    // Don't bother sending for empty input fields (don't require all to be filled out)
    if (input.dataset.metric && input.value) {
        // call metric logic
        const response = await fetch('/metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                metric_type: input.dataset.metric,
                value: input.value,
            })
        });
        const responseData = await response.json();

        if (responseData.success) {
            alert('Saved!');
        }
    } else if (input.dataset.checkin) {
        // TODO: call checkin logic
    }
}

/**
 * Marks a habit as complete/incomplete & updates the UI accordingly.
 * @async
 * @param {HTMLInputElement} checkbox - The checkbox that was clicked 
 * @param {number} habitId - The ID of the habit to update
 * @returns {Promise<void>} 
 */
async function markHabitComplete(checkbox, habitId) {
    // Fetch sends a request to flask server
    // POSTing to a dynamic URL like /complete_habit/7 => Translation: "Hey, mark habit 7 as complete"
    // If .checked == True  -> user just checked it
    // If .checked == False -> user just un-checked it

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

            // TODO: CLEAN NOTES
        // Mark un-complete => DELETE HabitCompletion from today
        } else {
            // Note: Built this to accept any date via query parameter (the "?=.." thing) for future flexibility
            // but currently we only ever delete today's completion from our main dashboard
            // So the route CAN handle any date, but our JS will stick to today
            const todayDateOnly = new Date().toISOString().split('T')[0]; // Gives format like "2025-06-26"

            const response = await fetch(`/habits/${habitId}/completions?date=${todayDateOnly}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
            });
            const responseData = await response.json(); // Wait for JSON parsing

            // DO something with our response data
            // Runs AFTER fetch + JSON parsing - not in a nested callback anymore
            if (responseData.success) {
                // un-apply effect/styling (update DOM)
                const textSpan = checkbox.nextElementSibling; // Grabs span right after checkbox element
                if (textSpan) {
                    textSpan.classList.remove('line-through', 'text-gray-400');
                }
            } else {
                console.error('Error un-marking habit complete:', responseData.message);
            }
        }
    } catch (error) {
        // Network/fetch errors for either case
        // With .then, we'd need .catch() at the end of each promise chain
        console.error('Error during habit completion request:', error);
    }
}

// Update time display in real-time
function getCurrentTimeString() {
    let date = new Date(); // First we need to get today's date obj
    let hours = date.getHours();
    let minutes = date.getMinutes();
    
    // Pad times & stitch together
    // TODO: Helper!!
    let paddedHours = hours.toString().padStart(2, '0');
    let paddedMinutes = minutes.toString().padStart(2, '0');
    let timeString = `${paddedHours}:${paddedMinutes}`;
    
    return timeString;
}

function updateClock() {
    let timeDisplay = document.querySelector('#time-display');
    timeDisplay.textContent = getCurrentTimeString(); // use getCurrentTimeString to call that & inject that value
}

// Get weather info via API, orchestrates our sun movement
async function getWeatherInfo() {
    const tempDisplay = document.querySelector('#weather-temp');
    const sunsetDisplay = document.querySelector('#weather-sunset');
    const city = "London";
    const units = "metric";

    try {
        tempDisplay.textContent = "Loading weather info...";

        const response = await fetch(`/api/weather/${city}/${units}`) // TODO: NOTES: GET is default method for fetch

        if (!response.ok) {
            throw new Error(`Weather API failed: ${response.status}`);
        }
        weatherInfo = await response.json();

        // Extract desired vals from weatherInfo data
        const temp = Math.round(weatherInfo.main.temp);
        const sunset = weatherInfo.sys.sunset;
        const desc = weatherInfo.weather[0].description.toLowerCase();

        const weatherConditions = {
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
        // Terms: variable declaration that stores the result of a complex expression
        const emoji = Object.entries(weatherConditions).find(
            ([key]) => desc.includes(key)
        )?.[1] ?? '🌡️'; // "?? '🌡️'" <= Nullish coalescing: fallback if nothing found
        
        // Convert sunset time to date & local
        // TODO: use new datetime helpers!!
        const sunsetTime = new Date(sunset * 1000); // comes in Unix-style, so convert first
        const sunsetFormatted = sunsetTime.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });

        // Display temp with units & formatted sunset time
        tempDisplay.textContent = `${temp}°${units === 'metric' ? 'C' : 'F'} ${emoji}`;
        sunsetDisplay.textContent = `Sunset: ${sunsetFormatted} 🌅`;

    } catch (error) {
        console.error('Weather fetch failed:', error);
        tempDisplay.textContent = "Weather unavailable";
        sunsetDisplay.textContent = "Sunset: --:--";
    }
}

function updateSunPosition() {
    if (weatherInfo) {
        const now = Math.floor(Date.now() / 1000); // convert to seconds to compare to what API gave
        cachedSunPos = calcSunPosition(weatherInfo.sys.sunrise, weatherInfo.sys.sunset, now);
        drawSun(cachedSunPos.x, cachedSunPos.y);
    }
}
// Handle calculation only of new sun position in arc
/**
 * Calculates normalized sun position along arc for the current time
 * @param {number} sunrise - Sunrise time in ms (Unix)
 * @param {number} sunset - Sunset time in ms (Unix)
 * @param {number} now - Current time in ms (Unix)
 * @returns {{x: number, y: number}} Normalized coordinates (0-1) for sun position
 * @description
 * - X represents progress through the day (0 = sunrise, 1 = sunset)
 * - Y uses sine curve to create natural arc (0 at horizon, peak at noon)
 * - Want to extend for moon calculation using night hours later
 */
function calcSunPosition(sunrise, sunset, now) {
    // Calculate horizontal progress through daylight hours (0-1)
    const xVal = (now - sunrise) / (sunset - sunrise);
    // Create arc using sine curve
    const yVal = Math.sin(xVal * Math.PI);

    /** Notes for adding our moon too:
     *  Calc becomes: (now - todaySunset) / (tomorrowSunrise - todaySunset)
     *  Conditionally re-use functions:
     *  if (now < tomorrowSunrise) -> calc/draw moon
     *  else                       -> calc draw sun
     *  Add moon phases later
     */
    // Debug: console.log(`Current time: ${now} | Sunrise: ${sunrise} | Sunset: ${sunset} | Progress thru day: ${(now-sunrise)/(sunset-sunrise)}`);
    return { x: xVal, y: yVal }
}

// Sun drawing constants
const SUN_CONFIG = {
    RADIUS: 10,
    RAY_COUNT: 8,
    RAY_LENGTH: 15,
    RAY_OFFSET: 5, // gap between sun & its rays
    COLOR: 'orange'
};

/**
 * Draws a sun with rays at normalized coordinates (0-1 range)
 * @param {number} x - Normalized x position (0=sunset, 1=sunset)
 * @param {number} y - Normalized y position (sine arc)
 */
function drawSun(x, y) {
    const canvas = document.querySelector('#sun-canvas');
    const ctx = canvas.getContext('2d');

    // Convert normalized coordinates to canvas pixels
    const canvasX = x * canvas.width;
    const canvasY = y * canvas.height;
    
    // Set up coordinate system with bottom-left origin
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.scale(1, -1);
    ctx.translate(0, -canvas.height);

    // Draw main sun body
    ctx.fillStyle = SUN_CONFIG.COLOR;
    ctx.beginPath();
    ctx.arc(canvasX, canvasY, SUN_CONFIG.RADIUS, 0, 2 * Math.PI);
    ctx.fill();

    // Draw sun rays
    ctx.strokeStyle = SUN_CONFIG.COLOR;
    for (let i = 0; i < SUN_CONFIG.RAY_COUNT; i++) {
        const angle = (i * 2 * Math.PI) / SUN_CONFIG.RAY_COUNT;
        const startX = canvasX + (SUN_CONFIG.RADIUS + 5) * Math.cos(angle);
        const startY = canvasY + (SUN_CONFIG.RADIUS + 5) * Math.sin(angle);
        const endX = canvasX + (SUN_CONFIG.RADIUS + SUN_CONFIG.RAY_LENGTH) * Math.cos(angle);
        const endY = canvasY + (SUN_CONFIG.RADIUS + SUN_CONFIG.RAY_LENGTH) * Math.sin(angle);
    
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    }
    ctx.restore(); // reset canvas to point of .save()
}

export function init() {
    // Guard
    const hasWeatherSection = document.querySelector('.weather-section');
    const hasTimeEntry = document.querySelector('#time-entry-modal');
    const hasHabits = document.querySelector('.habit-checkbox');
    if (!hasWeatherSection && !hasTimeEntry && !hasHabits) return;

    // Event listeners for page
    document.addEventListener('change', (e) => {
        if (e.target.matches('.habit-checkbox')) {
            // Pass checkbox element, data-habit-id value
            markHabitComplete(e.target, e.target.dataset.habitId);
        }
        // Handles saving of Daily Check-In inputs (only weight, steps, & movement so far though)
        else if (e.target.matches('input[data-metric]')) {
            saveData(e.target);
        }
    });

    // Intention <span>
    // TODO: Condense when we adapt editTableField to work for both
    document.addEventListener('dblclick', (e) => {
        if (e.target.matches('#intention-text')) {
            editIntention(e.target);
        }
    });

    document.addEventListener('click', (e) => {
        const modal = document.querySelector('#time-entry-modal');

        if (e.target.matches('#save-entry-btn')) {
            saveTimeEntry(e.target);
        }
        else if (e.target.matches('#time-entry-modal-btn')) {
            modal?.showModal();
        }
        else if (e.target.matches('#time-entry-modal-close-btn')) {
            const form = modal?.querySelector('form');
            form?.reset();
            modal?.close()
        }
    });
    // Weather setup
    if (hasWeatherSection) {
        getWeatherInfo();    // Cache weather data
        updateSunPosition(); // Draw sun immediately
        setInterval(getWeatherInfo, 1*60*60*1000);  // Update weather every hour
        setInterval(updateSunPosition, 10*60*1000); // Update sun from weatherInfo every 10 mins => 10*60*1000
    }
    // Clock setup
    if (document.querySelector('#time-display')) {
        setInterval(updateClock, 30 * 1000);
        updateClock();
    }
}

export { calcSunPosition };