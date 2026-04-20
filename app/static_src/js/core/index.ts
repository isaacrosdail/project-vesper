import { formatToUserTimeString } from '../shared/datetime';
import { initHabitForm, initMetricsForm, initTaskForm, initTimeEntryForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { userStore } from '../shared/services/userStore';
import { fetchWeatherData } from '../shared/services/weather-service';
import { makeToast } from '../shared/ui/toast';
import { randFloat, randInt } from '../shared/utils';
import { FormDialog, WeatherResult } from '../types';

// Weather widget state
let weatherInfo: WeatherResult | null = null;

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
    try { // TODO: why try/catch here? api already throws, no?
        const row = checkbox.closest('.item-row');
        const streakCountSpan = row?.querySelector<HTMLSpanElement>('.streak-count');
        // const streakIcon = row?.querySelector('.streak-icon');
        const listItem = row?.closest<HTMLLIElement>('.item');
        if (!row || !streakCountSpan || !listItem) {
            console.error('.item-row parent for checkbox not found')
            return;
        }
        const streakValue = streakCountSpan.dataset['streakCount'];
        let streakCount = (streakValue && streakValue !== '') ? parseInt(streakValue, 10) : 0;

        if (checkbox.checked) {
            const response = await api.habitCompletions.post(habitId);
            streakCount++;
            updateProgressBar('habits', response.data.progress);
        } else {
            const response = await api.habitCompletions.deleteToday(habitId);
            streakCount--;
            updateProgressBar('habits', response.data.progress);
        }
        streakCountSpan.dataset['streakCount'] = String(streakCount);
        listItem?.classList.toggle('completed', checkbox.checked);
        streakCountSpan.textContent = (streakCount > 0) ? String(streakCount) : '';
    } catch (error) {
        makeToast('Failed to update habit status', 'error');
        checkbox.checked != checkbox.checked;
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
    try {
        const response = await api.tasks.toggleComplete(taskId, checkbox.checked);
        const listItem = checkbox.closest('.item');
        listItem?.classList.toggle('completed');
        updateProgressBar('tasks', response.data.progress);
    } catch (error) {
        makeToast('Failed to update task status', 'error');
        checkbox.checked != checkbox.checked;
    }
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

    tempDisplay.textContent = `${temp}°${tempUnit} ${emoji} (${city}, ${country})`;
    tempDisplay.innerHTML = `
        ${temp}°${tempUnit}
        <svg class="icon"><use href="#${emoji}"></use></svg>
         - ${city}
    `;
    sunsetDisplay.textContent = `Sunset ${sunsetFormatted}`;
}

export function calcCelestialBodyPos(startTime: number, endTime:
number, now: number): { x: number, y: number } {
    const progress = (now - startTime) / (endTime - startTime);
    const clampedProgress = Math.max(0, Math.min(1, progress));

    const x = clampedProgress;
    const y = Math.sin(clampedProgress * Math.PI); // sin curve: 0 -> 1 -> 0

    return { x, y };
}

function updateSky() {
    if (!weatherInfo) return; // TODO: use that circuit breaker pattern thing?
    const { sunrise, sunset } = weatherInfo;
    const now = Math.floor(Date.now() / 1000);
    const isDay = now >= sunrise && now <= sunset;

    // Sky gradient
    const card = document.querySelector('#greeting-card');
    if (isDay) {
        card.style.setProperty('--sky-top', '#4a90d9');
        card.style.setProperty('--sky-bottom', '#87ceeb');
    } else {
        card.style.setProperty('--sky-top', '#0a1628');
        card.style.setProperty('--sky-bottom', '#1a2a4a');
    }

    // Sun/moon position — reuse your existing calcCelestialBodyPos
    const startTime = isDay ? sunrise : (now > sunset ? sunset : sunset - 86400);
    const endTime = isDay ? sunset : (now > sunset ? sunrise + 86400 : sunrise);
    const pos = calcCelestialBodyPos(startTime, endTime, now);

    // Drive a CSS element instead of canvas
    card.style.setProperty('--celestial-x', `${pos.x * 100}%`);
    card.style.setProperty('--celestial-y', `${pos.y * 100}%`);
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

// TODO: buggy, would use browser tz, no?
/**
 * Initializes the live clock display and updates it every 30 seconds.
 */
function initClock() {
    const timeDisplay = document.querySelector<HTMLElement>('#time-display');
    if (!timeDisplay) return;

    const updateClock = () => {
        timeDisplay.textContent = formatToUserTimeString(new Date());
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
        // renderer = new CelestialRenderer('#sky-canvas');
        getWeatherInfo();         // Cache weather data
        // updateCelestialBodyPos(); // Draw sun immediately
        updateSky();

        setInterval(getWeatherInfo, 1*60*60*1000);  // Update weather every hour
        setInterval(updateSky, /*5 * 60 * 1000*/6000); // Update sun from weatherInfo every 5 mins => 5*60*1000

        // // TODO: ResizeObserver!!
        // window.addEventListener('resize', () => {
        //     clearTimeout(resizeTimeout);
        //     resizeTimeout = setTimeout(redrawCanvas, 100); // debounce redraw
        // });
    } catch (error) {
        console.error(`Weather widget init failed: ${error}`)
    }
}

export function init() {
    updateProgressBar('habits');
    updateProgressBar('tasks');

    initCheckboxHandlers();
    initWeatherSection();
    initClock();

    const taskDialog = document.querySelector<FormDialog>('#tasks-entry-homepage-modal');
    const timeEntryDialog = document.querySelector<FormDialog>('#time_entries-entry-homepage-modal');
    const habitDialog = document.querySelector<FormDialog>('#habits-entry-homepage-modal');
    const metricDialog = document.querySelector<FormDialog>('#daily_metrics-entry-homepage-modal');
    if (!taskDialog || !timeEntryDialog || !habitDialog || !metricDialog) {
        console.warn('index.ts init: missing FormDialog(s)')
        return;
    }
    initTaskForm(taskDialog);
    initTimeEntryForm(timeEntryDialog);
    initHabitForm(habitDialog)
    initMetricsForm(metricDialog)

    // TODO: Need to add?
    // const leetCodeRecordsDialog = document.querySelector('#leet_code_records-entry-homepage-modal');
    // initLeetCodeRecordForm(leetCodeRecordsDialog);
}