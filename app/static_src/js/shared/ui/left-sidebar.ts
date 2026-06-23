

export function initLeftSidebar() {
    const sidebar = document.querySelector('.left-sidebar');
    if (!sidebar) {
        return;
    }
    const sidebarToggle = document.querySelector('#sidebar-toggle');
    const wrapper = document.querySelector('.wrapper');
    if (!wrapper || !sidebarToggle) {
        console.error('initLeftSidebar: missing sidebar-toggle/wrapper');
        return;
    }
    sidebarToggle.addEventListener('click', () => wrapper.classList.toggle('sidebar-open'));
}
