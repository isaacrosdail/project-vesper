// Bundler => auto-runner
// Custom tooltip behavior

/**
 * To use for a given element:
 * Add class 'tooltip' for styling
 * Add 'data-tip' attr with desired tooltip text
 */

document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggers = document.querySelectorAll('.tooltip');

    // Add listener to each tooltip
    tooltipTriggers.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            // Get button's position on screen
            const tooltip = document.createElement('div');
            tooltip.id = 'tooltip';
            tooltip.className = 'tooltip-popup';
            tooltip.setAttribute('role', 'tooltip'); // For a11y
            tooltip.setAttribute('aria-hidden', 'false');
            element.setAttribute('aria-describedby', tooltip.id) // Needs to be on trigger, not tooltip itself
            tooltip.textContent = element.getAttribute('data-tip'); // get text from HTML's data attr

            const tooltipPos = e.target.getBoundingClientRect(); // gives us position info for triggers
            const buttonCenterX = (tooltipPos.left + tooltipPos.right) / 2; // gives us dist from end to center for carrot
            tooltip.style.position = 'fixed';
            tooltip.style.left = tooltipPos.left + 'px';
            tooltip.style.top = tooltipPos.bottom + 'px';
            tooltip.style.zIndex = '1000'; // TODO: Consider dropping to 100-199 range to adhere to z-index notes in app.css
            document.body.appendChild(tooltip);

            const tooltipRect = tooltip.getBoundingClientRect();
            let arrowX = buttonCenterX - tooltipRect.left; // calc carrot position inside tooltip
            tooltip.style.setProperty('--carrot-pos', `${arrowX}px`);
        });
        element.addEventListener('mouseleave', () => {
            // Wipe tooltip on leave
            const tooltip = document.querySelector('#tooltip');
            tooltip?.remove();
        });
    });
});