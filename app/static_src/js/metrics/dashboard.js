
export function init() {
    if (!document.querySelector('#metrics-dashboard-table')) return;
    
    document.querySelectorAll('.tabs button').forEach(btn => {
        btn.addEventListener('click', () => {
            console.log(`Button ${btn.dataset.tab} clicked`);
            // hide all panels & remove active
            document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(p => p.hidden = true);
            // show selected
            const cls = 'tab-' + btn.dataset.tab;
            const panel = document.querySelector(`#${cls}`);
            if (panel) {
                btn.classList.add('active');
                panel.hidden = false
            };
        });
    });
}
