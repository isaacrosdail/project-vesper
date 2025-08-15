// Bundler => auto-runner
// Custom tooltip behavior

/**
 * To use for a given element:
 * Add class 'tooltip' for styling
 * Add 'data-tip' attr with desired tooltip text
 */

document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggers = document.querySelectorAll('.tooltip');
    // debug console.log(`Found ${tooltipTriggers.length} triggers`);

    // Add listener to each tooltip
    tooltipTriggers.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            // Get button's position on screen
            const tooltip = document.createElement('div');
            tooltip.id = 'tooltip';
            tooltip.className = 'tooltip-popup';
            tooltip.setAttribute('role', 'tooltip'); // For a11y
            tooltip.setAttribute('aria-hidden', 'false');
            tooltip.setAttribute('aria-describedby', tooltip.id)
            tooltip.textContent = element.getAttribute('data-tip'); // get text from HTML's data attr

            const tooltipPos = e.target.getBoundingClientRect(); // gives us position info for triggers
            const buttonCenterX = (tooltipPos.left + tooltipPos.right) / 2; // gives us dist from end to center for carrot
            tooltip.style.position = 'fixed';
            tooltip.style.left = tooltipPos.left + 'px';
            tooltip.style.top = tooltipPos.bottom + 'px';
            tooltip.style.zIndex = '1000';
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