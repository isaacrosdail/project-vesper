// Auto-runner, attaches DOM listeners on DOMContentLoaded at top level

function setMobileNavOpen(shouldBeOpen: boolean, navMobileContainer: HTMLElement, hamburgerBtn: HTMLElement): void {
    navMobileContainer.classList.toggle('is-open', shouldBeOpen);
    hamburgerBtn.classList.toggle('is-open', shouldBeOpen);
    hamburgerBtn.setAttribute('aria-expanded', String(shouldBeOpen)); // toggle aria-expanded value

    if (shouldBeOpen) {
        navMobileContainer.removeAttribute('inert');
        navMobileContainer.querySelector('a')?.focus();
    } else {
        navMobileContainer.setAttribute('inert', '');
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const navMobileContainer = document.querySelector<HTMLElement>('#nav-mobile-container');
    const hamburgerBtn = document.querySelector<HTMLButtonElement>('.hamburger-btn');
    const profileModal = document.querySelector<HTMLDialogElement>('.profile-modal');
    const mq = window.matchMedia('(max-width: 768px)'); // uses a media query obj in JS, syncs JS state with CSS breakpoint

    document.addEventListener('click', (e) => {
        if (!(e.target instanceof HTMLElement)) return;

        // Profile button
        if (profileModal) {
            if (e.target.matches('.profile-btn')) profileModal.showModal();
            if (e.target.matches('#close-profile-modal-btn')) profileModal.close();
        }

        // Mobile nav
        if (!navMobileContainer || !hamburgerBtn) return;
        const isOpen = navMobileContainer.classList.contains('is-open');

        if (e.target.matches('.hamburger-btn')) {
            setMobileNavOpen(!isOpen, navMobileContainer, hamburgerBtn);
            return;
        }
        if (isOpen && !e.target.closest('.nav-mobile')) {
            setMobileNavOpen(false, navMobileContainer, hamburgerBtn);
            return;
        }

    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            profileModal?.close();
        }
    });

    // Reset nav state when switching to desktop
    mq.addEventListener('change', (e) => {
        if (!navMobileContainer || !hamburgerBtn) return;
        // True when window <= 768px
        if (!e.matches && navMobileContainer.classList.contains('is-open')) {
            setMobileNavOpen(false, navMobileContainer, hamburgerBtn);
        }
    });
});