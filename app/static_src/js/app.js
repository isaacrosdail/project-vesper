// Attempting to grab user info (namely for timezone for now) in a maintainable way
import { userStore } from './shared/userStore.js';

// Entry point for shared JS
import './shared/navbar.js';
import './shared/tables.js';
import './shared/theme-manager.js';
import './shared/toast.js';
import './shared/tooltip.js';

// Import page-specific modules
import { init as initCore } from './core/index.js';
import { init as initGroceries } from './groceries/dashboard.js';
import { init as initHabits } from './habits/dashboard.js';
import { init as initTasks } from './tasks/dashboard.js';


// Init user data upon app load
async function initApp() {
    try {
        await userStore.fetch();
        console.log('User timezone loaded:', userStore.data.timezone);
    } catch (error) {
        console.warn('Error loading user timezone: ', error);
        // Fall back to browser timezone
    }
    
    // Initialize all page modules (which in turn self-determine if they should init)
    // TODO: NOTES: Study, also look into dependency orchestration (init order matters?)
    initCore();
    initGroceries();
    initHabits(); 
    initTasks();
}

// Start the app (runs when we load <script> in base.html)
// 1. Page loads
// 2. app.js executes
// 3. initApp() runs
// 4. userStore.fetch() gets timezone for user
initApp();