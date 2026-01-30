// App root module to act as app's bootstrapper

import { userStore } from './shared/services/userStore.js';
import { makeToast } from './shared/ui/toast.js';

// Load shared components
import './shared/navbar.js';
import './shared/tables.js';
import './shared/ui/theme-manager.js';
import './shared/ui/toast.js';
import './shared/ui/tooltip.js';
import './shared/charts.js';
import './shared/ui/modal-manager.js';
import './shared/ui/context-menu.js';
import './shared/forms.js';
import './shared/ui/dropdown.js';

// Import page-specific modules
import { init as initCore } from './core/index.js';
import { init as initStyleRef } from './style-reference.js';
import { init as initGroceries } from './groceries/dashboard.js';
import { init as initHabits } from './habits/dashboard.js';
import { init as initTasks } from './tasks/dashboard.js';
import { init as initTimeTracking } from './time_tracking/dashboard.js';
import { init as initMetrics } from './metrics/dashboard.js';
import { init as initRegisterPage } from './register.js';
import { init as initTasksWebPage } from './tasks_web.js';


const initRegistry = {
    "main.home": () => initCore(),
    "devtools.style_reference": () => initStyleRef(),
    "groceries.dashboard": () => initGroceries(),
    "habits.dashboard": () => initHabits(),
    "tasks.dashboard": () => initTasks(),
    "time_tracking.dashboard": () => initTimeTracking(),
    "metrics.dashboard": () => initMetrics(),
    "auth.register": () => initRegisterPage(),

    "main.tasks_web": () => initTasksWebPage(),
};

export async function initMain() {
    await initUserStore();
    showToastsFromFlask();

    const page = document.documentElement.dataset['page'];
    if (page && page in initRegistry) {
        initRegistry[page as keyof typeof initRegistry]();
    }
}

async function initUserStore() {
    if (document.documentElement.dataset['authenticated'] !== 'true') return;
    try {
        await userStore.fetch();
        if (!userStore.data?.timezone) {
            throw new Error('User store loaded without timezone. Invalid state');
        }
    } catch (error) {
        console.error('Failed to load userStore:', error);
        throw new Error('Failure: could not load userStore.');
    }
}

/**
 * Pop toasts from Flask's session to be presented, if any
 */
function showToastsFromFlask(): void {
    const toastRaw = document.body.dataset['toast'];
    if (toastRaw && toastRaw !== 'null') {
        const toast = JSON.parse(toastRaw);
        makeToast(toast.message, toast.type, 3000);
    }
}