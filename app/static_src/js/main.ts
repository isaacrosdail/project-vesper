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
import { init as initCore } from './home/index';
import { init as initGroceries } from './groceries/dashboard/dashboard';
import { init as initGroceriesData } from './groceries/data/data';
import { init as initHabits } from './habits/dashboard';
import { init as initMetrics } from './metrics/dashboard';
import { init as initRegisterPage } from './register';
import { init as initLoginPage } from './login';
import { init as initStyleRef } from './style-reference/style-reference';
import { init as initTasks } from './tasks/dashboard';
import { init as initTimeTracking } from './time_tracking/dashboard';

import { init as initRecipesPage } from './groceries/recipes/recipes';
import { init as initShoppingPage } from './groceries/shopping/shopping';
import { init as initPillarsPage } from './pillars';
import { init as initProfileSidebar } from './shared/ui/profile-sidebar';
import { initLeftSidebar } from './shared/ui/left-sidebar';
import { ApiError } from './shared/services/api';
import { refreshMe } from './shared/services/userState.svelte';
import { mount } from 'svelte';
import ConfirmDialog from './shared/components/ConfirmDialog.svelte';
import ContextMenu from './shared/components/ContextMenu.svelte';
import Toaster from './shared/components/Toaster.svelte';
import HotkeysHelp from './HotkeysHelp.svelte';

const initRegistry = {
    "main.home": () => initCore(),
    "devtools.style_reference": () => initStyleRef(),
    "groceries.dashboard": () => initGroceries(),
    "groceries.data": () => initGroceriesData(),
    "groceries.shopping": () => initShoppingPage(),
    "habits.dashboard": () => initHabits(),
    "tasks.dashboard": () => initTasks(),
    "time_tracking.dashboard": () => initTimeTracking(),
    "metrics.dashboard": () => initMetrics(),
    "auth.register_form": () => initRegisterPage(),
    "auth.login_form": () => initLoginPage(),

    // Prototyping stuff
    "groceries.recipes": () => initRecipesPage(),
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
    const authenticated = document.documentElement.dataset['authenticated'] === 'true';
    if (authenticated) await refreshMe();

    mount(HotkeysHelp, { target: document.body });
    mount(ConfirmDialog, { target: document.body });
    mount(ContextMenu, { target: document.body });
    mount(Toaster, { target: document.body });
    showToastsFromFlask();

    const page = document.documentElement.dataset['page'];
    if (page && page in initRegistry) {
        initRegistry[page as keyof typeof initRegistry]();
    } else {
        console.warn(`data-page "${page}" has no init registered`);
    }

    if (authenticated) initProfileSidebar();
    initLeftSidebar();
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