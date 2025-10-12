import { formatTimeString } from '../shared/datetime.js';
import { getJSInstant } from '../shared/datetime.js';
import { fetchWeatherData } from '../shared/services/weather-service.js';
import { calcCelestialBodyPos, CelestialRenderer, setupCanvas } from '../shared/canvas.js';
import { makeToast } from '../shared/ui/toast.js';
import { apiRequest } from '../shared/services/api.js';
import { randInt, randFloat } from '../shared/numbers.js';


// Global caches
let weatherInfo = null;
let currentCanvasState = null;
let resizeTimeout = null;
let renderer;

let isInitialRender = true;

function updateProgressBar(module, percent = null, completed = null, total = null){
    const section = document.querySelector(`.${module}-progress`);
    const fill = section.querySelector('.progress-bar-fill');
    const progressText = section.querySelector('.progress-text');

    const fillPercentage = (percent !== null) ? percent : fill.dataset.progress;
    const remainingPercentage = 100 - fillPercentage;

    // Update dataset
    fill.dataset.progress = fillPercentage;
    if (completed !== null && total !== null) {
        fill.dataset.completed = completed;
        fill.dataset.total = total;
    }
    // Prevent transition effect for initial page load
    if (isInitialRender) {
        fill.style.transition = 'none';
        fill.style.transform = `scaleX(${remainingPercentage / 100})`;
        isInitialRender = false;
        // re-enable transitions next tick
        requestAnimationFrame(() => fill.style.transition = '');
    } else {
        fill.style.transform = `scaleX(${remainingPercentage / 100})`;
    }

    // Update text display
    const textCompleted = (completed !== null) ? completed : fill.dataset.completed;
    const textTotal = (total !== null) ? total : fill.dataset.total;
    progressText.textContent = `${textCompleted} of ${textTotal}`;

    // Trigger confetti at 100%
    const numCompleted = Number(completed)
    const numTotal = Number(total)
    if (numTotal > 0 && numCompleted === numTotal && percent !== null) {
        triggerConfetti(section);
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
    try {
        // Mark complete => POST HabitCompletion
        const completedAtUTC = getJSInstant();  // Get instant user clicks "done"

        const row = checkbox.closest('.item-row'); // scope query to right <label> row
        const emojiSpan = row.querySelector('.habit-streak');
        const listItem = row.closest('.item'); // grab <li>
        let streakCount = parseInt(emojiSpan.dataset.streakCount, 10);

        if (checkbox.checked) {
            const url = `/habits/${habitId}/completions`;
            const data = { completed_at: completedAtUTC };

            apiRequest('POST', url, (responseData) => {
                streakCount += 1;
                emojiSpan.dataset.streakCount = streakCount;

                listItem?.classList.toggle('completed');
                emojiSpan.textContent = `🔥${streakCount}`;
                const prog = responseData.data.progress;
                console.log(prog)
                updateProgressBar('habits', prog[4], prog[2], prog[3])
            }, data);
        } else {
            const todayDateOnly = new Intl.DateTimeFormat('en-CA').format(new Date());
            const url = `/habits/${habitId}/completions?date=${todayDateOnly}`;

            apiRequest('DELETE', url, (responseData) => {
                streakCount -= 1;
                emojiSpan.dataset.streakCount = streakCount;

                listItem?.classList.toggle('completed');
                if (streakCount > 0) {
                    emojiSpan.textContent = `🔥${streakCount}`;
                } else {
                    emojiSpan.textContent = "";
                }
                const prog = responseData.data.progress;
                updateProgressBar('habits', prog[4], prog[2], prog[3])
            });
        }
    } catch (error) {
        console.error('Error during habit completion request:', error);
    }
}
async function markTaskComplete(checkbox, taskId) {
    const completedAtUTC = getJSInstant();
    const url = `/tasks/tasks/${taskId}`;

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
    apiRequest('PATCH', url, (responseData) => {
        const listItem = checkbox.closest('.item');
        listItem?.classList.toggle('completed');
        const prog = responseData.data.progress;
        console.log(prog)
        updateProgressBar('tasks', prog[4], prog[2], prog[3],)
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

function triggerConfetti(progressBar) {
    const emitter = progressBar.querySelector('.emitter');
    if (!emitter) {
        console.log(`No emitter found for: ${progressBar}`);
        return;
    }
    // 1. Random number of dots
    const numDots = randInt(8, 12)
    // 2. Append to emitter

    const shapeClasses = ['star', 'circle', 'diamond', 'parallelogram', 'triangle'];
    // 3. Create and append random number of 'dot' divs
    for (let i = 0; i < numDots; i++) {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        emitter.appendChild(dot);

        // 4. First randomly generate values for Bezier curve arcs
        const endX = randInt(-150, 150); // horizontal spread
        const endY = randInt(-120, -200); // how high or low it ends
        const fallY = randInt(200, 250);
        const controlX = randInt((endX * 0.4), (endX * 0.6));
        const controlY = randInt((endY - 30), (endY + 30));
        /* 
            M x y -> move to (x,y)
            Q cx cy x y -> Quad Bezier: control point (cx,cy) and endpoint (x,y)
            C c1x c1y c2x c2y x y -> Cubic Bezier (two control points, one end)
        */
        const path = `M 0 0 Q ${controlX} ${controlY} ${endX} ${endY} T ${endX} ${fallY}`;
        const animationTime = randFloat(1.5, 3)
        const animationDelay = randFloat(0.9, 1)
        const shape = shapeClasses[i % shapeClasses.length];
        console.log(`Shape:${shape}, i: ${i}`)
        dot.classList.add(shape);

        dot.style.width = `${randInt(3, 7)}px`;
        dot.style.height = `${randInt(3, 7)}px`;
        dot.style.offsetPath = `path('${path}')`;
        dot.style.animation = `followPath ${animationTime}s cubic-bezier(0.25, 0.7, 0.9, 0.3) ${animationDelay} forwards`;
        dot.style.animation += `, tumble ${randFloat(0.6, 1.5)}s linear infinite`;

        // Clean up after
        dot.addEventListener('animationend', () => {
            dot.remove();
        });
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

    updateProgressBar('habits');
    updateProgressBar('tasks');

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