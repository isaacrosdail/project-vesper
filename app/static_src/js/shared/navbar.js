// Auto-runner, attaches DOM listeners on DOMContentLoaded at top level
// Optional chaining defends against issues on pages w/o a navbar?
// Safe to import in index.js (entry point for shared/)

window.addEventListener('DOMContentLoaded', () => {
    const mobilenavlinks = document.querySelector('#mobilenav');
    const modal = document.querySelector('#settings-modal');
    const mq = window.matchMedia('(max-width: 640px)'); // uses a media query obj in JS, syncs JS state with CSS breakpoint
    const hamburgerBtn = document.querySelector('#hamburger-btn');

    document.addEventListener('click', (e) => {
        // Toggle mobile nav
        if (e.target.matches('#hamburger-btn')) {
            mobilenavlinks?.classList.toggle('is-open');
            const isOpen = mobilenavlinks?.classList.contains('is-open'); // set proper bool for is-open state
            hamburgerBtn.setAttribute('aria-expanded', String(isOpen)); // toggle aria-expanded value 
            if (isOpen) mobilenavlinks.querySelector('a')?.focus(); // focus on first anchor el in nav
        }

        // TODO: Auto-close mobile-nav upon click elsewhere

        // Open settings modal
        if (e.target.matches('#settings-btn')) {
            // Optional chaining avoids null errors if modal is missing
            modal?.showModal(); // ESC key & blur automatically handled
        }
        // Close settings modal
        if (e.target.matches('#close-dev-modal-btn')) {
            modal?.close();
        }
    });

    // Reset nav state when switching to desktop (close, reset aria-expanded)
    mq.addEventListener('change', (e) => {
        // True when window <= 640px
        if (!e.matches) {
            mobilenavlinks.classList.remove('is-open');
            hamburgerBtn.setAttribute('aria-expanded', 'false');
        }
    });
});