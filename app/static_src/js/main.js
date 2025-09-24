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

// Import page-specific modules
import { init as initCore } from './core/index.js';
import { init as initStyleRef } from './style-reference.js';
import { init as initGroceries } from './groceries/dashboard.js';
import { init as initHabits } from './habits/dashboard.js';
import { init as initTasks } from './tasks/dashboard.js';

const initRegistry = {
    "main.home": () => initCore(),
    "devtools.style_reference": () => initStyleRef(),
    "groceries.dashboard": () => initGroceries(),
    "habits.dashboard": () => initHabits(),
    "tasks.dashboard": () => initTasks(),
};

export async function initMain() {
    await initUserStore();
    showToastsFromFlask();

    const page = document.documentElement.dataset.page;
    if (initRegistry[page]) {
        initRegistry[page]();
    }
}

async function initUserStore() {
    try {
        await userStore.fetch();
        // console.log('User timezone loaded:', userStore.data.timezone);
    } catch (error) {
        if (!userStore.data) {
            userStore.data = {};
        }
        // Fall back to browser timezone
        userStore.data.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        // console.log(`Fallback to browser timezone: `, userStore.data.timezone);
    }
}

function showToastsFromFlask() {
    // Pop toasts from Flask's session to present, if any
    const toastRaw = document.body.dataset.toast;
    if (toastRaw && toastRaw !== 'null') {
        const toast = JSON.parse(toastRaw);
        makeToast(toast.message, toast.type, 3000);
    }
}