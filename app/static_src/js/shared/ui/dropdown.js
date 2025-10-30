
const dropdowns = document.querySelectorAll('.dropdown');

document.addEventListener('click', (e) => {
    if (e.target.matches('.dropdown-toggle')) {
        const dropdown = e.target.closest('.dropdown');
        dropdown.classList.toggle('is-open');
    } else if (e.target.closest('.dropdown-menu button')) {
        console.log("check")
        const dropdown = e.target.closest('.dropdown');
        const toggle = dropdown.querySelector('.dropdown-toggle .dropdown-toggle-label');
        toggle.textContent = e.target.textContent.trim();
        dropdown.classList.remove('is-open');
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