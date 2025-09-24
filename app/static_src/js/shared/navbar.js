// Auto-runner, attaches DOM listeners on DOMContentLoaded at top level

function toggleMobileNav(mobileNav, hamburgerBtn) {
    mobileNav?.classList.toggle('is-open');
    let isOpen = mobileNav?.classList.contains('is-open'); // set proper bool for is-open state
    hamburgerBtn.setAttribute('aria-expanded', String(isOpen)); // toggle aria-expanded value 
    if (isOpen) {
        mobileNav.removeAttribute('inert');
        mobileNav.querySelector('a')?.focus(); // focus on first anchor el in nav
    } else {
        mobileNav.setAttribute('inert', '');
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const mobileNav = document.querySelector('#nav-mobile-container');
    const modal = document.querySelector('.profile-modal');
    const mq = window.matchMedia('(max-width: 768px)'); // uses a media query obj in JS, syncs JS state with CSS breakpoint
    const hamburgerBtn = document.querySelector('.hamburger-btn');

    document.addEventListener('click', (e) => {
        let isOpen = mobileNav?.classList.contains('is-open');
        
        // Toggle mobile nav
        if (e.target.matches('.hamburger-btn')) {
            toggleMobileNav(mobileNav, hamburgerBtn);
        }

        // TODO: Auto-close mobile-nav upon click elsewhere
        // mobile nav is open + click wasnt in navbar
        if (isOpen && !e.target.closest('#mobilenav') && !e.target.matches('.hamburger-btn')) {
            toggleMobileNav(mobileNav, hamburgerBtn);
        }
        if (e.target.matches('.profile-btn')) {
            modal?.showModal();
        }
        if (e.target.matches('#close-profile-modal-btn')) {
            modal?.close();
        }
    });

    // Reset nav state when switching to desktop
    mq.addEventListener('change', (e) => {
        // True when window <= 768px
        if (mobileNav?.classList.contains('is-open') && !e.matches) {
            toggleMobileNav(mobileNav, hamburgerBtn);
        }
    });
});