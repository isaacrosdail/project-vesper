// App root module to act as app's bootstrapper

import { addToast } from './shared/components/Toaster.svelte';

// Load shared components
import './shared/charts';
import './shared/forms';
import './shared/navbar';
import './shared/tables';
import './shared/ui/theme-manager';
import './shared/ui/tooltip';

// Import page-specific modules
import { init as initCore } from './core/index';
import { init as initGroceries } from './groceries/dashboard';
import { init as initGroceriesData } from './groceries/data';
import { init as initHabits } from './habits/dashboard';
import { init as initMetrics } from './metrics/dashboard';
import { init as initRegisterPage } from './register';
import { init as initStyleRef } from './style-reference';
import { init as initTasks } from './tasks/dashboard';
import { init as initTimeTracking } from './time_tracking/dashboard';

import { init as initRecipesPage } from './groceries/recipes';
import { init as initTasksWebPage } from './tasks_web';
import { init as initPillarsPage } from './pillars';
import { init as initProfileSidebar } from './shared/ui/profile-sidebar';
import { initLeftSidebar } from './shared/ui/left-sidebar';
import { ApiError } from './shared/services/api';
import { refreshMe } from './shared/services/userState.svelte';
import { mount } from 'svelte';
import ConfirmDialog from './shared/components/ConfirmDialog.svelte';
import ContextMenu from './shared/components/ContextMenu.svelte';
import Toaster from './shared/components/Toaster.svelte';

const initRegistry = {
    "main.home": () => initCore(),
    "devtools.style_reference": () => initStyleRef(),
    "groceries.dashboard": () => initGroceries(),
    "groceries.data": () => initGroceriesData(),
    "habits.dashboard": () => initHabits(),
    "tasks.dashboard": () => initTasks(),
    "time_tracking.dashboard": () => initTimeTracking(),
    "metrics.dashboard": () => initMetrics(),
    "auth.register": () => initRegisterPage(),

    // Prototyping stuff
    "groceries.recipes": () => initRecipesPage(),
    "main.tasks_web": () => initTasksWebPage(),
    "main.pillars": () => initPillarsPage(),
};

window.addEventListener('unhandledrejection', (e) => {
    if (e.reason instanceof ApiError) {
        handleApiError(e.reason);
        e.preventDefault();
    } else {
        console.warn(`unhandledRejection: ${e.reason.message}`);
    }
});

function handleApiError(err: unknown) {
    if (err instanceof ApiError) {
        if (err.errors) {
            for (const [field, messages] of Object.entries(err.errors)) {
                messages.forEach(message => addToast(`${field}: ${message}`, '', 'error'));
            }
        } else {
            addToast(err.message, '', 'error');
        }
    } else {
        addToast("Unexpected error", '', 'error');
    }
}

export async function initMain() {
    await initUserState();
    mount(ConfirmDialog, { target: document.body });
    mount(ContextMenu, { target: document.body });
    mount(Toaster, { target: document.body });
    showToastsFromFlask();

    const page = document.documentElement.dataset['page'];
    if (page && page in initRegistry) {
        initRegistry[page as keyof typeof initRegistry]();
    }

    // Sidebar outright (depends on userStore)
    initProfileSidebar();
    initLeftSidebar();
}

async function initUserState() {
    if (document.documentElement.dataset['authenticated'] !== 'true') return;
    await refreshMe();
}

/**
 * Pop toasts from Flask's session to be presented, if any
 */
function showToastsFromFlask(): void {
    const toastRaw = document.body.dataset['toast'];
    if (toastRaw && toastRaw !== 'null') {
        const toast = JSON.parse(toastRaw);
        addToast(toast.title, toast.message, toast.type);
    }
}