
// init dropdowns (using popover API + anchor positioning, this is just needed to "pair" via css properties)
/**
 * Generic dropdown behavior for any [popover]-based dropdown on the page.
 * 
 * Open/close, light-dismiss, and ESC are handled via native Popover API
 * (popovertarget on the toggle). It does not manage open state. (???)
 * Adds 3 things:
 *   1. Anchor position (glue menu to its toggle)
 *   2. Chevron flip    (reflect open/closed visually)
 *   3. Selection contract (emit `dropdown:change`, then auto-close)
 * 
 * Markup to use:
 *   Trigger:
 *     <button class="dropdown-toggle" popovertarget="ID">
 *   Menu:
 *     <div popover id="ID" class="dropdown-menu">
 *       <button data-value="..">...</button>
 *     </div>
 * 
 * Each option must have data-value attribute
 * 
 * Emits: `dropdown-change
 *     CustomEvent dispatched on the menu element when an option is clicked.
 *     detail.value = the option's data value.
 *     Consumers listen on the specific menu they care about.
 * 
 * Does NOT do the actual positioning math -> that lives in CSS for dropdown-menu
 * 
 */
document.querySelectorAll('.dropdown-toggle').forEach(btn => {
    // Pair each toggle to its menu via popovertarget id
    const targetId = btn.getAttribute('popovertarget');
    const menu = document.querySelector(`#${targetId}`);
    if (!menu) return;

    // Tying anchor positioning together
    btn.style.setProperty('anchor-name', `--${targetId}`);
    menu.style.setProperty('position-anchor', `--${targetId}`);

    // For chevron flip; reads from Popover API's toggle event so platform tracks state
    menu.addEventListener('toggle', (e: ToggleEvent) => {
        const isOpen = e.newState === 'open';
        btn.querySelector('.dropdown-toggle-chevron svg').classList.toggle('flip', isOpen);
    });

    // Emit custom change event so listeners can access selected option via event obj directly??
    menu.addEventListener('click', (e) => {
        const opt = e.target.closest('[data-value]');
        if (!opt) return;

        menu.dispatchEvent(new CustomEvent('dropdown:change', {
            detail: { value: opt.dataset.value }
        }));
        menu.hidePopover();
    });
});
