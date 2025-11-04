
/**
 * Initialize "click eye icon for password/text toggle".
 * 
 * Conventions:
 * - Buttons must have a [data-password-toggle] attribute
 * - whose value = the ID of the <input type="password">
 * Script will:
 * - Find the target <input>
 * - Toggle type="password" <-> type="text" on click
 * - Reflect toggle state in `aria-pressed`
 * 
 * @example
 * <input id="pwd1" type="password">
 * <button data-password-toggle="pwd1">(eye)</button>
 */
export function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll<HTMLElement>('[data-password-toggle]');
    if (toggleButtons.length === 0) return;

    toggleButtons.forEach(btn => {
        const inputId = btn.dataset.passwordToggle;
        if (!inputId) return; // apparently JS *might* search for '#undefined'? unhinged.
        const input = document.querySelector<HTMLInputElement>(`#${inputId}`);
        if (!input) return;
        btn.setAttribute('aria-pressed', input.type === 'text' ? 'true' : 'false')

        btn.addEventListener('click', () => {
            const isPressed = btn.getAttribute('aria-pressed') === 'true';
            input.type = isPressed ? 'password' : 'text';
            btn.setAttribute('aria-pressed', String(!isPressed));
        })
    })
}

initPasswordToggles();