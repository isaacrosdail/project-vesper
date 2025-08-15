// tasks/dashboard.js  
import { setupModal } from '../shared/modal-manager.js';

export function init() {
    // Guard
    if (!document.querySelector('#add-task-btn')) return;

    setupModal('add-task-modal', 'add-task-btn', '/tasks/', 'Task created!');
}