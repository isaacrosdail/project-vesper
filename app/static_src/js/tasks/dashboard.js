// // tasks/dashboard.js  
// import { setupModal } from '../shared/modal-manager.js';

export function init() {
    // Guard
    if (!document.querySelector('#tasks-dashboard-table')) return;

    document.querySelector('#is_frog').addEventListener('change', (e) => {
        document.querySelector('#due_date').required = e.target.checked;
    });

}