
// init dropdowns (using popover API + anchor positioning, this is just needed to "pair" via css properties)
document.querySelectorAll('.dropdown-toggle').forEach(btn => {
    const targetId = btn.getAttribute('popovertarget');
    const menu = document.querySelector(`#${targetId}`);
    if (!menu) return;
    btn.style.setProperty('anchor-name', `--${targetId}`);
    menu.style.setProperty('position-anchor', `--${targetId}`);
    // For chevron flip
    menu.addEventListener('toggle', (e: ToggleEvent) => {
        const isOpen = e.newState === 'open';
        btn.querySelector('.dropdown-toggle-chevron svg').classList.toggle('flip', isOpen);
    });
});
