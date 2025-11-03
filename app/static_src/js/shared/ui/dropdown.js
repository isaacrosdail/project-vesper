
const dropdowns = document.querySelectorAll('.dropdown');

document.addEventListener('click', (e) => {
    if (e.target.matches('.dropdown-toggle')) {
        const dropdown = e.target.closest('.dropdown');
        dropdown.classList.toggle('is-open');
    } else if (e.target.closest('.dropdown-menu button')) {
        const dropdown = e.target.closest('.dropdown');
        dropdown.classList.remove('is-open');
        // Only update label if dropdown is replaceable
        if (dropdown.querySelector('.dropdown-toggle[data-replaceable]')) {
            const toggle = dropdown.querySelector('.dropdown-toggle .dropdown-toggle-label');
            toggle.textContent = e.target.textContent.trim();
        }
    } else {
        dropdowns.forEach(el => {
            el.classList?.remove('is-open');
        })
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        dropdowns.forEach(el => {
            el.classList?.remove('is-open');
        });
    }
});