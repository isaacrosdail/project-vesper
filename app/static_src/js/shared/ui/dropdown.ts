
const dropdowns = document.querySelectorAll('.dropdown');

document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;

    if (target.matches('.dropdown-toggle')) {
        const dropdown = target.closest<HTMLDivElement>('.dropdown')!;
        dropdown.classList.toggle('is-open');

    } else if (target.closest('.dropdown-menu button')) {
        const dropdown = target.closest<HTMLDivElement>('.dropdown')!;
        dropdown.classList.remove('is-open');

        // Only update label if dropdown is replaceable
        if (dropdown.querySelector('.dropdown-toggle[data-replaceable]')) {
            const toggle = dropdown.querySelector<HTMLSpanElement>('.dropdown-toggle .dropdown-toggle-label')!;
            toggle.textContent = target.textContent!.trim();
        }

    } else {
        dropdowns.forEach(el => {
            el.classList.remove('is-open');
        })
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        dropdowns.forEach(el => {
            el.classList.remove('is-open');
        });
    }
});