
window.addEventListener('DOMContentLoaded', () => {
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const mobileNav = document.getElementById('mobile-nav');

    if (hamburgerBtn && mobileNav) {
        hamburgerBtn.addEventListener('click', () => {
            mobileNav.classList.toggle('show');
        })
    }
})

// Resize event listener to hide our mobile-nav (handles our mobile-nav.show state)
let lastWidth = 640;
// Throttle our resize check
let currentTime = Date.now(); // returns ms since 1970
let lastCheckTime = currentTime - 200; // Pretend it's been 200ms since last check

window.addEventListener('resize', function() {
    currentTime = Date.now();
    if (currentTime - lastCheckTime >= 200){
        console.log('Resize triggered!')
        const mobileNav = document.getElementById('mobile-nav');
        // When resize fires, check if window.innerWidth is above or below 640px
        // Crossing TO desktop
        if (mobileNav && window.innerWidth > 640 && lastWidth <= 640) {
            // Remove the .show class from mobile-nav
            mobileNav.classList.remove('show');
        }
        // Crossing TO mobile
        if (mobileNav && window.innerWidth < 640 && lastWidth >= 640) {
            mobileNav.classList.remove('show');
        }
        lastWidth = window.innerWidth;

        lastCheckTime = Date.now();
    }
})