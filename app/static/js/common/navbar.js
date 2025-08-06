
window.addEventListener('DOMContentLoaded', () => {
    const mobileNav = document.getElementById('mobile-nav');
    const modal = document.getElementById('my-modal');

    document.addEventListener('click', (e) => {
        const t = e.target

        // TODO: Extract these notes!!
        /** Optional chaining operator ('?')
         * Old JS:
         * if (modal && modal.showModal) {
         *     modal.showModal();
         * }
         * 
         * Modern:
         *  modal?.showModal();  <= if modal is null or undefined, it just silently returns undefined instead of exploding :D
         * And yes, we can chain multiple like: user?.profile?.picture?.url (nested obj/property checks)
         */

        // Toggle mobile nav
        if (t.matches('#hamburger-btn')) {
            mobileNav?.classList.toggle('show'); // ? is the optional chaining operator
        }

        // Baby's First Modal
        // Open modal
        if (t.matches('#my-btn')) {
            // Trying out <dialog> element stuff
            // What's this do? => dialog.returnValue = "...";
            modal?.showModal(); // ESC key & blur automatically handled :P
        }
    });
})

/**
 * Cleans up .show class from mobile-nav when viewport exceeds 640px
 * Media query handles setting mobile-nav.show display to none though
 * TODO: Do we even use/need this anymore? Tidy up
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