
// Constant for daily-intention-submit button
const dailyIntentionSubmitBtn = document.getElementById("intention-submit");
// Variables for daily-intention-text and daily-intention-result
let dailyIntentionText = document.getElementById("daily-intention-text");
let dailyIntentionResult = document.getElementById("intention-display");

// Show edit mode input field
function enableEdit() {
    document.getElementById("intention-display").classList.add("hidden"); // Hide intention display (span we dblclick)
    document.getElementById("intention-edit").classList.remove("hidden"); // Show edit input field
    document.getElementById("intention-input").focus();
}

// Want the value of daily-intention-text to become daily-intention-result, then hide daily-intention-edit again
dailyIntentionSubmitBtn.onclick = () => {
    // Get daily-intention text from input using element id
    const value = document.getElementById("intention-input").value;

    // POST request to DB via fetch
    fetch(`/daily-intentions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intention: value })
    })
    .then(response => response.json()) // convert response to json so we can use it
    .then(data => {
        // Where we handle SUCCESS -> update the DOM, etc.
        // 
        document.getElementById("intention-text").textContent = value;
        // And hide the input text box and submit button
        document.getElementById("intention-display").classList.remove("hidden");
        document.getElementById("intention-edit").classList.add("hidden");
    })
    .catch(error => {
        // Handling errors
        console.error('Failed to save/update: ', error);
    })
}


// Function that activates when checkbox for anchor habits are checked, indicating completion
// Function will then use fetch() to trigger POST to tell Flask to update DB
function markHabitComplete(checkbox, habitId) {
    // Fetch sends a request to flask server
    // POSTing to a dynamic URL like /complete_habit/7
    // Translation: "Hey, mark habit 7 as complete"

    // If .checked == True  -> user just checked it
    // If .checked == False -> user just un-checked it
    const isDone = checkbox.checked;

    // Now need to break our original PATCH request into two different requests.
    if (checkbox.checked) {
        // POST a new HabitCompletion record
        fetch(`/habits/${habitId}/completions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        })
        // Awaits Flask's response; .json() converts it from raw response to usable JS obj ( {success: true })
        .then(response => {
            if (response.ok) {
                // Immediately apply strikethrough effect
                const textSpan = checkbox.nextElementSibling; // Grabs the span right after checkbox element
                if (textSpan) {
                    textSpan.classList.add("line-through", "text-gray-400");
                }
            }
        })
        // Error Catching (eg, network fails, Flask throws error) // Could later show a popup, retry, etc.
        // If network fails or Flask throws an error, you'll see it here
        .catch(error => {
            console.error('Error marking habit complete:', error);
        });
    } else {
        // DELETE the existing HabitCompletion record
        fetch(`/habits/${habitId}/completions/today`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        // Awaits Flask's response; .json() converts it from raw response to usable JS obj ( {success: true })
        .then(response => {
            if (response.ok) {
                // Immediately remove strikethrough effect
                const textSpan = checkbox.nextElementSibling; // Grabs the span right after checkbox element
                if (textSpan) {
                    textSpan.classList.remove("line-through", "text-gray-400");
                }
            }
        })
        .catch(error => {
            console.error('Error un-marking habit complete:', error);
        });
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
    // Get the element by id
    let timeDisplay = document.getElementById("time-display");
    // use getCurrentTimeString to call that and inject that value
    timeDisplay.textContent = getCurrentTimeString();
}

// Get weather info via API
async function getWeatherInfo() {
    const tempDisplay = document.getElementById('weather-temp');
    const sunsetDisplay = document.getElementById('weather-sunset');
    const city = "London";
    const units = "metric";

    tempDisplay.textContent = "Loading weather info...";

    // Async fetch to call our Flask API endpoint/weather/<city>/<units>
    const response = await fetch(`/api/weather/${city}/${units}`) // GET is the default method, so we just need this here!
    // weatherInfo is our resultant json containing all the info we need
    const weatherInfo = await response.json();

    // use weather info - to start, grab temp & sunset time
    const temp = Math.round(weatherInfo.main.temp);
    const sunset = weatherInfo.sys.sunset;
    const desc = weatherInfo.weather[0].description.toLowerCase();

    // Pass sunrise & sunset times to our updateSunPosition function once
    updateSunPosition(weatherInfo.sys.sunrise, weatherInfo.sys.sunset);

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
}

// Fun function to make a sun move across the weather widget as the day progresses! :D
function updateSunPosition(sunrise, sunset) {
    // To find our normalized x value for the position of our sun
    const now = Date.now() / 1000; // Current time as Unix timestamp
    const xVal = (now - sunrise) / (sunset - sunrise);
    const yVal = Math.sin(xVal * Math.PI);  // Using a sin curve to give us our arc for the sun, fits well between 0 and 1

    drawSun(xVal, yVal);
}

// Getting started with Canvas
function drawSun(x, y) {

    // First, translate our values from updateSunPosition to scale to canvas size
    const canvasX = x * 100; // 0-1 becomes 0-100
    const canvasY = 100 - (y * 100); // 0-1 becomes 0-100 (flipped - since canvas's (0,0) is at the top left!)
    const canvas = document.getElementById('sun-canvas');
    // ctx is a common abbreviation for context - the drawing interface object
    const ctx = canvas.getContext('2d'); // Canvas can do diff types of drawing 2D graphics or 3D (WebGL?) // 2D here tells it "I want to draw 2D stuff like circles, lines, etc."
    
    // Clear the previous sun first!
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = 'orange';
    // beginPath() - Canvas draws using "paths" - You start a new path, draw some shapes, then tell it to actually render
    ctx.beginPath();
    // ctx.arc(x, y, radius, start angle, end angle);
    // x, y represent the center point coords - where on the canvas to put the circle
    // radius 10 says "10 pixels from center to edge"
    // start angle is where to start drawing (0 = rightmost point)
    // end angle is where to stop drawing (2pi = full circle)
    ctx.arc(canvasX, canvasY, 10, 0, 2 * Math.PI);
    ctx.fill();
}

window.onload = async () => {
    setInterval(updateClock, 30 * 1000); // 30 seconds
    updateClock();

    await getWeatherInfo();
}