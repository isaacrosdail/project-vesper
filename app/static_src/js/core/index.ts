import { formatTimeString, getJSInstant } from '../shared/datetime.js';
import { calcCelestialBodyPos, CelestialRenderer, CelestialType, setupCanvas } from '../shared/canvas.js';
import { apiRequest } from '../shared/services/api.js';
import { fetchWeatherData } from '../shared/services/weather-service.js';
import { userStore } from '../shared/services/userStore.js';
import { randInt, randFloat } from '../shared/numbers.js';

import { WeatherResult } from '../types.js';

// Weather widget state
let weatherInfo: WeatherResult | null = null;
let currentCanvasState: { bodyType: CelestialType; x: number; y: number; } | null = null;
let renderer: CelestialRenderer | null = null;
let resizeTimeout: ReturnType<typeof setTimeout> | undefined;

// Progress bar UI state
let isInitialRender = true;

type ProgressBarModule = 'tasks' | 'habits';

type UpdateProgressBarOptions = {
    percent?: number;
    completed?: number;
    total?: number;
};

/**
 * Updates a progress bar's fill width, label text, & completion effects.
 * 
 * If `percent`, `completed`, or `total` are omitted, falls back to values stored in the `.progress-bar-fill` dataset attributes.
 * 
 * - Disables CSS transition for initial render to avoid an unwanted animation
 * - toggles a 'surging' class when nearly complete
 * - triggers confetti when progress reaches 100%
 * 
 * @param module - Which progress bar to update ('tasks' | 'habits')
 * @param options - Progress data from backend calculation or manual overrides
 * @param options.percent - Completion percentage
 * @param options.completed - Number of completed items
 * @param options.total - Total number of items
 */
function updateProgressBar(module: ProgressBarModule, options: UpdateProgressBarOptions = {}): void {
    const section = document.querySelector<HTMLDivElement>(`.${module}-progress`);
    const fill = section?.querySelector<HTMLDivElement>('.progress-bar-fill');
    const progressText = section?.querySelector<HTMLDivElement>('.progress-text');
    if(!fill || !section || !progressText) {
        console.error('Missing section/fill/progressText div(s)');
        return;
    }

    const { percent = null, completed = null, total = null } = options;

    const fillPercentage: number = (percent !== null) ? percent : Number(fill.dataset['percent']);

    // Update dataset
    fill.dataset['percent'] = String(fillPercentage);
    if (completed !== null && total !== null) {
        fill.dataset['completed'] = String(completed);
        fill.dataset['total'] = String(total);
    }
    // Prevent transition effect for initial page load
    if (isInitialRender) {
        fill.style.transition = 'none';
        fill.style.transform = `scaleX(${fillPercentage / 100})`;
        isInitialRender = false;
        // re-enable transitions next tick
        requestAnimationFrame(() => fill.style.transition = '');
    } else {
        fill.style.transform = `scaleX(${fillPercentage / 100})`;
    }

    // Update text display
    const numCompleted = (completed !== null) ? completed : Number(fill.dataset['completed']);
    const numTotal = (total !== null) ? total : Number(fill.dataset['total']);
    progressText.textContent = `${numCompleted} of ${numTotal}`;


    // Trigger surging + pulsing effects at either 90% completion OR 1 task/habit remaining
    if (fillPercentage >= 90 || (numTotal - numCompleted) === 1) {
        fill.classList.add('surging')
    } else {
        fill.classList.remove('surging');
    }

    // Trigger confetti at 100%
    if (numTotal > 0 && numCompleted === numTotal && percent !== null) {
        const progressBar = section.querySelector<HTMLElement>('.progress-bar');
        if (progressBar) {
            triggerConfetti(progressBar);
        } else {
            console.warn('Progress bar element not found for confetti trigger.');
        }
    }
}

/**
 * Marks a habit as complete/incomplete via API & updates the UI.
 * 
 * @param checkbox - Checkbox that was toggled.
 * @param habitId - Habit ID from `data-habit-id`.
 * 
 * @remarks
 * Updates on success:
 * - Toggles `.completed` class on `.item` element
 * - Updates streak count in `.habit-streak` span (data attr + emoji text)
 */
async function markHabitComplete(checkbox: HTMLInputElement, habitId: string): Promise<void> {
    try {
        // Mark complete => POST HabitCompletion
        const completedAtUTC = getJSInstant();

        const row = checkbox.closest('.item-row');
        const emojiSpan = row?.querySelector<HTMLSpanElement>('.habit-streak');
        const listItem = row?.closest<HTMLLIElement>('.item');
        if (!row || !emojiSpan || !listItem) {
            console.error('.item-row parent for checkbox not found')
            return;
        }
        const streakValue = emojiSpan.dataset['streakCount'];
        let streakCount = (streakValue && streakValue !== '') ? parseInt(streakValue, 10) : 0;

        if (checkbox.checked) {
            const url = `/habits/${habitId}/completions`;
            const data = { completed_at: completedAtUTC };

            apiRequest('POST', url, data, {
                onSuccess: (responseData) => {
                    streakCount += 1;
                    emojiSpan.dataset['streakCount'] = String(streakCount);

                    listItem?.classList.toggle('completed');
                    emojiSpan.textContent = `🔥${streakCount}`;
                    updateProgressBar('habits', responseData.data.progress);
                }
            });
        } else {
            const todayDateOnly = new Intl.DateTimeFormat('en-CA').format(new Date());
            const params = new URLSearchParams({ date: todayDateOnly });
            const url = `/habits/${habitId}/completions?${params}`;

            apiRequest('DELETE', url, null, {
                onSuccess: (responseData) => {
                    streakCount -= 1;
                    emojiSpan.dataset['streakCount'] = String(streakCount);

                    listItem?.classList.toggle('completed');
                    emojiSpan.textContent = (streakCount > 0) ? `🔥${streakCount}` : "";
                    updateProgressBar('habits', responseData.data.progress);
                }
            });
        }
    } catch (error) {
        console.error('Error during habit completion request:', error);
    }
}

/**
 * Marks a task as done/not done via API & updates the UI.
 * 
 * @param checkbox - Checkbox that was toggled.
 * @param taskId - Task ID from `data-task-id`.
 * 
 * @remarks
 * Updates on success:
 * - Toggle `.completed` class on `.item` element
 */
async function markTaskComplete(checkbox: HTMLInputElement, taskId: string): Promise<void> {
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
    apiRequest('PATCH', url, data, {
        onSuccess: (responseData) => {
            const listItem = checkbox.closest<HTMLLIElement>('.item');
            listItem?.classList.toggle('completed');
            updateProgressBar('tasks', responseData.data.progress);
        }
    });
}

/**
 * Fetches weather data from API and updates the weather widget display.
 * Runs on page load & refreshes hourly.
 * 
 * @remarks
 * Updates two DOM elements: #weather-temp and #weather-display
 * 
 * Caches result in global `weatherInfo` for use by celestial body positioning.
 * 
 * Location (and in future units) are read from userStore (user prefs).
 * 
 * @throws Logs error and returns early if userStore data is unavailable
 */
async function getWeatherInfo() {
    const tempDisplay = document.querySelector('#weather-temp');
    const sunsetDisplay = document.querySelector('#weather-sunset');
    if (!tempDisplay || !sunsetDisplay) {
        console.warn('Weather display elements not found in DOM');
        return;
    }
    if (!userStore.data) {
        console.error('Weather widget cannot initialize; userStore data unavailable');
        return;
    }
    const { city, country, units } = userStore.data;

    tempDisplay.textContent = "Loading weather info...";
    weatherInfo = await fetchWeatherData(city, country, units);

    const { temp, emoji, sunsetFormatted } = weatherInfo;
    const tempUnit = units === 'metric' ? 'C' : 'F';
    tempDisplay.textContent = `${temp}°${tempUnit} ${emoji}`;
    sunsetDisplay.textContent = `Sunset: ${sunsetFormatted} 🌅`;
}

/**
 * Calculates and renders sun/moon position based on current time relative to sunrise/sunset.
 * 
 * Updates global `currentCanvasState` and triggers canvas redraw.
 */
function updateCelestialBodyPos() {
    if (!weatherInfo) return;
    const { sunrise, sunset } = weatherInfo;
    if (!sunrise || !sunset) {
        console.debug('Sunrise/sunset data null, skipping celestial body position update');
        return;
    }

    const now = Math.floor(Date.now() / 1000);

    let startTime: number;
    let endTime: number;
    let bodyType: CelestialType = 'moon';

    if (now >= sunrise && now <= sunset) {
        // Daytime
        bodyType = 'sun';
        startTime = sunrise;
        endTime = sunset;
    } else if (now > sunset) {
        // Night (after sunset)
        startTime = sunset;
        endTime = sunrise + (24 * 60 * 60); // next sunrise
    } else {
        // Last night (before sunrise)
        startTime = sunset - (24 * 60 * 60); // previous sunset
        endTime = sunrise;
    }
    const position = calcCelestialBodyPos(startTime, endTime, now);
    currentCanvasState = { bodyType, x: position.x, y: position.y };
    redrawCanvas();
}

/**
 * Redraws the celestial body canvas at current position.
 * Called after window resize to prevent distortion.
 */
function redrawCanvas() {
    setupCanvas();
    if (currentCanvasState && renderer) {
        renderer.draw(
            currentCanvasState.x, 
            currentCanvasState.y, 
            currentCanvasState.bodyType
        );
    }
}

/**
 * Spawns animated confetti particles at the (right) end of a progress bar.
 * 
 * @param el - Element whose position determines confetti spawn point
 * @remarks
 * Animation behavior:
 * - Spawns several dozen particles with randomized shapes
 * - Particles follow Bezier curves (arc upwards, then fall)
 * - Each auto-removes itself upon animationend
 * - Respects `prefers-reduced-motion`
 * 
 * Requires:
 * - `#confetti-layer` element in document for z-index stacking/overflow handling
 * - CSS custom property `--confetti-size-base` for responsive sizing
 */
function triggerConfetti(el: HTMLElement) {

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const progressBarBox = el.getBoundingClientRect();
    const confettiLayer = document.querySelector('#confetti-layer');
    if (!confettiLayer) {
        console.error('Confetti emitter div not found');
        return;
    }

    // SETTINGS
    const shapeClasses = ['star', 'circle', 'diamond', 'parallelogram', 'triangle'];
    const numDots = randInt(15, 40)
    const baseSize = parseFloat(getComputedStyle(document.documentElement)
        .getPropertyValue('--confetti-size-base'));

    // Generate each confetti dot
    for (let i = 0; i < numDots; i++) {
        const dot = document.createElement('div');
        dot.classList.add('dot', shapeClasses[i % shapeClasses.length]!);

        // Position dot at right edge of progress-bar
        dot.style.position = 'absolute';
        dot.style.left = `${progressBarBox.right}px`;
        dot.style.top = `${progressBarBox.top + progressBarBox.height / 2}px`;

        // Generate Bezier path (curved + falling)
        const endX = randInt(-150, 150);    // horizontal arc/spread
        const endY = randInt(-120, -250);   // apex
        const fallY = randInt(200, 250);    // fall distance
        const controlX = randInt(endX * 0.4, endX * 0.6);
        const controlY = randInt(endY - 30, endY + 30);
        const path = `M 0 0 Q ${controlX} ${controlY} ${endX} ${endY} T ${endX} ${fallY}`;

        // Animation Timings
        const animationTime = randFloat(1.5, 3);
        const animationDelay = randFloat(0.9, 1);
        const tumbleSpeed = randFloat(0.6, 1.5);
        const scale = baseSize * randFloat(4, 5);    // size scaling (semi-responsive)

        // Assign styles & animations
        dot.style.setProperty('--scale', String(scale));
        dot.style.offsetPath = `path('${path}')`;
        dot.style.animation = 
            `follow-path ${animationTime}s cubic-bezier(0.25, 0.7, 0.9, 0.3) ${animationDelay} forwards, ` +
            `tumble ${tumbleSpeed}s linear infinite`;
        
        // Insert into confetti layer & tidy up when done
        confettiLayer.appendChild(dot);
        dot.addEventListener('animationend', () => dot.remove());
    }
}

/**
 * Attaches change event listeners to habit and task checkboxes.
 */
function initCheckboxHandlers() {
    const hasCheckboxes = document.querySelector('.habit-checkbox, .task-checkbox');
    if (!hasCheckboxes) {
        console.debug('Checkbox handlers not initialized: no checkboxes found.');
        return;
    }

    document.addEventListener('change', (e) => {
        const target = e.target as HTMLInputElement;
        if (target.matches('.habit-checkbox')) {
            const habitId = target.dataset['habitId'];
            if (!habitId){
                console.error('Habit checkbox missing data-habit-id');
                return;
            }
            markHabitComplete(target, habitId);
        }
        if (target.matches('.task-checkbox')) {
            const taskId = target.dataset['taskId'];
            if (!taskId) {
                console.error('Task checkbox missing data-task-id');
                return;
            }
            markTaskComplete(target, taskId);
        }
    });
}

/**
 * Initializes the live clock display and updates it every 30 seconds.
 */
function initClock() {
    const timeDisplay = document.querySelector<HTMLElement>('#time-display');
    if (!timeDisplay) return;

    const updateClock = () => {
        timeDisplay.textContent = formatTimeString(new Date());
    }

    updateClock();
    setInterval(updateClock, 30 * 1000);
}

/**
 * Initializes weather widget with live data and celestial body animation arc.
 * Sets up hourly weather refresh and periodic sun/moon position updates.
 */
function initWeatherSection() {
    const hasWeatherSection = document.querySelector('.weather-info');
    if (!hasWeatherSection) {
        console.debug('initWeatherSection failed: Missing .weather-info section');
        return;
    }

    try {
        renderer = new CelestialRenderer('#sky-canvas');
        getWeatherInfo();         // Cache weather data
        updateCelestialBodyPos(); // Draw sun immediately

        setInterval(getWeatherInfo, 1*60*60*1000);  // Update weather every hour
        setInterval(updateCelestialBodyPos, /*5 * 60 * 1000*/6000); // Update sun from weatherInfo every 5 mins => 5*60*1000

        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(redrawCanvas, 100); // debounce redraw
        });
    } catch (error) {
        console.error(`Weather widget init failed: ${error}`)
    }
}

export function init() {
    console.debug('Initializing dashboard widgets...');

    updateProgressBar('habits');
    updateProgressBar('tasks');

    initCheckboxHandlers();
    initWeatherSection();
    initClock();
}