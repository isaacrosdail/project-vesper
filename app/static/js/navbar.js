
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

window.addEventListener('resize', function() {
    // When resize fires, check if window.innerWidth is above or below 640px
    // console.log(`Current width: ${lastWidth}`);
    if (window.innerWidth > 640 && lastWidth <= 640) {
        console.log(`CROSSED!`)
    }
    if (window.innerWidth < 640 && lastWidth >= 640) {
        console.log('CROSSED BACK!')
    }
    lastWidth = window.innerWidth;
})