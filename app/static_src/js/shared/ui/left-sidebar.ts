

export function initSidebar() {
    const sidebarToggle = document.querySelector('#sidebar-toggle');
    const wrapper = document.querySelector('.wrapper');
    if (!wrapper || !sidebarToggle) {
        console.error('setupSidebar: missing sidebar-toggle/wrapper');
        return;
    }
    // Toggle
    sidebarToggle.addEventListener('click', () => wrapper.classList.toggle('sidebar-open'));
}