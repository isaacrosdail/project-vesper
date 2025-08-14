

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
    const categoryElement = card.querySelector('#category');
    const durationElement = card.querySelector('#duration');
    const descriptionElement = card.querySelector('#description');

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
/**
 * Converts a span element into an input field for inline editing
 * @param {HTMLElement} element - The span element containing text to edit
 * @description
 * - Replaces span content with size-appropriate input field pre-populated with original text
 * - Save changes on blur/enter (if not empty) or reverts to original text
 */
function editIntention(element) {
    // Grab current text of element
    const originalText = element.textContent.trim();

    // Replace innerHTML of span with input field & pre-populate with current text
    element.innerHTML = `<input type="text" value="${originalText}" size="${originalText.length + 2}">`;
    // Grab the input element inside our span element & focus it
    const input = element.querySelector('input');
    input.focus();

    // Now set up event listeners for our blur event (to save => call updateIntention)
    input.addEventListener('blur', function() {
        if (input.value.trim() != '') {
            updateIntention(element, input.value); // pass our new text
        } else {
            element.innerHTML = originalText; // Don't save if input is left empty
        }
    });
    // Trigger blur on enter key
    input.addEventListener('keydown', function(event) {
        if (event.key == 'Enter') {
            input.blur();
        }
    });
}


async function updateIntention(element, newValue) {
    try {
        // Convert to modern async/await variant
        // 1. Replace fetch and first .then
        const response = await fetch('/daily-intentions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ intention: newValue })
        });

        const responseData = await response.json();

        if (responseData.success) {
            // Where we handle SUCCESS -> update the DOM, etc.
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
                unit: input.dataset.unit
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
        if (checkbox.checked) {
            // Replaces our fetch & part of our first .then:
            const response = await fetch(`/habits/${habitId}/completions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });
            const responseData = await response.json(); // convert json to obj -> Wait for JSON parsing before moving on

            // DO something with our response data
            // (In the .then version, this would be inside the second .then() callback)
            if (responseData.success) {
                // apply effect/styling (update DOM)
                const textSpan = checkbox.nextElementSibling; // Grabs span right after checkbox element
                if (textSpan) {
                    textSpan.classList.add('line-through', 'text-gray-400');
                }
            } else {
                // Error handling from Flask route
                console.error('Error marking habit complete:', responseData.message);
            }

        // Mark un-complete => DELETE HabitCompletion from today
        } else {
            // Note: Built this to accept any date via query parameter (the "?=.." thing) for future flexibility
            // but currently we only ever delete today's completion from our main dashboard
            // So the route CAN handle any date, but our JS will stick to today
            const today = new Date(); // Date() with no args defaults to current date and time
            const dateFormatted = today.toISOString().split('T')[0]; // Gives format like "2025-06-26"

            const response = await fetch(`/habits/${habitId}/completions?date=${dateFormatted}`, {
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
                // Error handling from Flask route
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
    
    // Pad times
    let paddedHours = hours.toString().padStart(2, '0');
    let paddedMinutes = minutes.toString().padStart(2, '0');
    // Template literal to conjoin
    let timeString = `${paddedHours}:${paddedMinutes}`;
    
    return timeString;
}

function updateClock() {
    let timeDisplay = document.querySelector('#time-display'); // Get the element by id
    timeDisplay.textContent = getCurrentTimeString(); // use getCurrentTimeString to call that and inject that value
}

// Get weather info via API, orchestrates our sun movement
async function getWeatherInfo() {
    const tempDisplay = document.querySelector('#weather-temp');
    const sunsetDisplay = document.querySelector('#weather-sunset');
    const city = "London";
    const units = "metric";

    try {
        tempDisplay.textContent = "Loading weather info...";

        // Async fetch to call our Flask API endpoint/weather/<city>/<units>
        const response = await fetch(`/api/weather/${city}/${units}`) // TODO: Note: GET is default method for fetch

        if (!response.ok) {
            throw new Error(`Weather API failed: ${response.status}`);
        }
        // Parse JSON response 
        weatherInfo = await response.json();

        // use weather info - to start, grab temp & sunset time
        const temp = Math.round(weatherInfo.main.temp);
        const sunset = weatherInfo.sys.sunset;
        const desc = weatherInfo.weather[0].description.toLowerCase();

        // Determine fitting emoji
        let emoji = '🌡️';
        if (desc.includes('thunder')) emoji = '⛈️';
        if (desc.includes('drizzle')) emoji = '🌦️';
        if (desc.includes('rain')) emoji = '🌧️';
        if (desc.includes('overcast')) emoji = '☁️';
        if (desc.includes('snow')) emoji = '❄️';
        if (desc.includes('mist') || desc.includes('fog')) emoji = '🌫️';
        if (desc.includes('clear')) emoji = '☀️';
        if (desc.includes('few clouds')) emoji = '🌤️';
        if (desc.includes('scattered') || desc.includes('broken')) emoji = '⛅';
        if (desc.includes('overcast')) emoji = '☁️';
        if (desc.includes('tornado')) emoji = '🌪️';
        
        // Convert sunset time to date & local
        const sunsetTime = new Date(sunset * 1000); // comes in Unix-style, so convert first
        const sunsetFormatted = sunsetTime.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });

        // Display temp with units
        tempDisplay.textContent = `${temp}°${units === 'metric' ? 'C' : 'F'} ${emoji}`;
        // Display formatted sunset time
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

    // Debug logging
    // console.log(`Current time: ${now} | Sunrise: ${sunrise} | Sunset: ${sunset} | Progress thru day: ${(now-sunrise)/(sunset-sunrise)}`);

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
 * Draws a sun with rays, centered at the specified normalized coordinates
 * @param {number} x - Normalized x position (0-1)
 * @param {number} y - Normalized y position (0-1)
 */
function drawSun(x, y) {
    const canvas = document.querySelector('#sun-canvas');

    // Get 2D drawing context (vs 3D WebGL context) // ctx is common abbreviation for 'context' - the drawing interface obj
    const ctx = canvas.getContext('2d'); 

    // Convert normalized coordinates (0-1) to actual canvas pixels
    // Makes the function work with any canvas size
    const canvasX = x * canvas.width; // 0-1 becomes 0-actualWidth
    const canvasY = y * canvas.height; // 0-1 becomes 0-actualHeight
    
    // Clear canvas & setup coordinate system
    ctx.clearRect(0, 0, canvas.width, canvas.height); // clear prior to transforms, using normal coords
    ctx.save(); // Save canvas state => saves: transform matrix (scale/translate/rotate), styles (fillStyle/strokeStyle/etc.), & clipping regions
                // NOT the actual drawn content
    ctx.scale(1, -1);                 // Flip y-axis
    ctx.translate(0, -canvas.height); // Move origin to bottom-left

    // Draw main sun body
    ctx.fillStyle = SUN_CONFIG.COLOR;
    ctx.beginPath(); // Start drawing new "path" - start a new path, draw some shapes, then tell it to actually render
    // arc(centerX, centerY, radius, startAngle, endAngle) - draws from 0 to 2pi for full circle
    ctx.arc(canvasX, canvasY, SUN_CONFIG.RADIUS, 0, 2 * Math.PI);
    ctx.fill();

    //Debug: Draw a dot for each of the sunrise and sunset points
    // console.log('Raw x, y from math:', x, y);
    // console.log('Canvas coordinates: ', canvasX, canvasY);
    // console.log('Canvas size: ', canvas.width, canvas.height);

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
    ctx.restore(); // Reset transforms to saved state
}

// Main event listeners
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.querySelector('#time-entry-modal');

    // Switch to event delegation pattern for habit checkboxes
    // Idea is: Apply listener to PARENT, then determine where event came from
    // Consolidate 'change' listener for both habit checkboxes & metric inputs
    // Now our parent becomes .content, so we need to change the querySelector
    document.addEventListener('change', (e) => {
        if (e.target.matches('.habit-checkbox')) {
            // event.target = the checkbox (what used to be 'this' in our inline onchange)
            // event.target.dataset.habitId = gets the data-habit-id value we added
            markHabitComplete(e.target, e.target.dataset.habitId);
        }
        // Handles saving of Daily Check-In inputs (only weight, steps, & movement so far though)
        else if (e.target.matches('input[data-metric]')) {
            saveData(e.target);
        }
    });

    document.addEventListener('dblclick', (e) => {
        // Dblclick for span of id intention-text
        if (e.target.matches('#intention-text')) {
            // Pass element e.target to turn into input
            editIntention(e.target);
        }
    });

    document.addEventListener('click', (e) => {
        // Click save-entry-btn to save time log entry
        if (e.target.matches('#save-entry-btn')) {
            saveTimeEntry(e.target); // pass in our button element and navigate from there
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
});

window.onload = async () => {
    setInterval(updateClock, 30 * 1000); // 30 seconds
    updateClock();

    await getWeatherInfo(); // Cache weather data
    updateSunPosition(); // Draw sun immediately

    setInterval(getWeatherInfo, 1*60*60*1000); // Update weather every hour
    setInterval(updateSunPosition, 10*60*1000); // Update sun from weatherInfo every 10mins 10*60*1000
}

// Make function(s) exportable for testing using Jest
if (typeof module !== 'undefined') {
    module.exports = { calcSunPosition };
}