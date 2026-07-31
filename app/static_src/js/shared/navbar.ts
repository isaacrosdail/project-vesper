import { required } from "./dom";

const navMobileContainer = required(document.querySelector<HTMLElement>('#nav-mobile-container'), '#nav-mobile-container');
const hamburgerBtn = required(document.querySelector<HTMLButtonElement>('.hamburger-btn'), '.hamburger-btn');
const backdrop = required(document.querySelector<HTMLElement>('#nav-backdrop'), '#nav-backdrop');
const mq = window.matchMedia('(max-width: 768px)'); // uses a media query obj in JS, syncs JS state with CSS breakpoint

let isMenuOpen = false;

function setMobileNav(open: boolean): void {
    if (open === isMenuOpen) return;
    isMenuOpen = open;
    navMobileContainer.classList.toggle('is-open', isMenuOpen);
    hamburgerBtn.classList.toggle('is-open', isMenuOpen);
    backdrop.classList.toggle('is-open', isMenuOpen);
    hamburgerBtn.setAttribute('aria-expanded', String(isMenuOpen)); // toggle aria-expanded value

    if (isMenuOpen) {
        navMobileContainer.removeAttribute('inert');
        navMobileContainer.querySelector('a')?.focus();
    } else {
        navMobileContainer.setAttribute('inert', '');
        hamburgerBtn.focus();
    }
}

hamburgerBtn.addEventListener('click', () => setMobileNav(!isMenuOpen));
backdrop.addEventListener('click', () => setMobileNav(false));

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isMenuOpen) setMobileNav(false);
});

// Close if viewport crosses into desktop layout
mq.addEventListener('change', (e) => {
    if (!e.matches && isMenuOpen) setMobileNav(false);
});
