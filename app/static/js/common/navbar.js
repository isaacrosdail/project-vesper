
window.addEventListener('DOMContentLoaded', () => {
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const mobileNav = document.getElementById('mobile-nav');

    if (hamburgerBtn && mobileNav) {
        hamburgerBtn.addEventListener('click', () => {
            mobileNav.classList.toggle('show');
        })
    }
})

/**
 * Cleans up .show class from mobile-nav when viewport exceeds 640px
 * Media query handles setting mobile-nav.show display to none though
 */
const DESKTOP_BREAKPOINT = 640;
const THROTTLE_DELAY = 200; // Throttle to every 200ms
let resizeTimer;

window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);

    /**
     * Throttled resize event handler
     * Removes mobile-nav.show when crossing to desktop viewport size
     */
    resizeTimer = setTimeout(() => {
        const mobileNav = document.getElementById('mobile-nav'); // Grab element
        if (mobileNav && window.innerWidth > DESKTOP_BREAKPOINT) { // Check if window size past our breakpoint for desktop
            // Remove the .show class from mobile-nav
            mobileNav.classList.remove('show');
        }
    }, THROTTLE_DELAY);
});