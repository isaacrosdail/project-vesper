
window.addEventListener('DOMContentLoaded', () => {
    const navlinks = document.querySelector('.navlinks');
    const modal = document.querySelector('#settings-modal');
    const mq = window.matchMedia('(max-width: 640px)'); // uses a media query obj in JS, syncs JS state with CSS breakpoint
    const hamburgerBtn = document.querySelector('#hamburger-btn');

    document.addEventListener('click', (e) => {
        // Toggle mobile nav
        if (e.target.matches('#hamburger-btn')) {
            navlinks?.classList.toggle('is-open'); // ? is the optional chaining operator
            const isOpen = navlinks?.classList.contains('is-open'); // set proper bool for is-open state
            hamburgerBtn.setAttribute('aria-expanded', String(isOpen)); // toggle aria-expanded value 
            if (isOpen) navlinks.querySelector('a')?.focus(); // focus on first anchor el in nav
        }

        // Open settings modal
        if (e.target.matches('#settings-btn')) {
            // Optional chaining avoids null errors if modal is missing
            modal?.showModal(); // ESC key & blur automatically handled
        }
    });

    // Reset nav state when switching to desktop (close, reset aria-expanded)
    mq.addEventListener('change', (e) => {
        // True when window <= 640px
        if (!e.matches) {
            navlinks.classList.remove('is-open');
            hamburgerBtn.setAttribute('aria-expanded', 'false');
        }
    });
});