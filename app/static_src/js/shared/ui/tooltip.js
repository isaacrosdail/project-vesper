// Bundler => auto-runner
// Custom tooltip behavior

/**
 * To use for a given element:
 * Add class 'tooltip' for styling
 * Add 'data-tip' attr with desired tooltip text
 */

export function showToolTip(targetEl, textContent) {
    const tooltip = document.createElement('div');
    tooltip.id = 'tooltip';
    tooltip.className = 'tooltip-popup';
    tooltip.setAttribute('role', 'tooltip'); // For a11y
    tooltip.setAttribute('aria-hidden', 'false');
    targetEl.setAttribute('aria-describedby', tooltip.id); // Needs to be on trigger, not tooltip itself
    tooltip.textContent = textContent;

    const targetElRect = targetEl.getBoundingClientRect(); // gives us position info for triggers
    const isTall = targetElRect.height > 80;
    const targetElCenterX = (targetElRect.left + targetElRect.right) / 2; // gives us dist from end to center for carrot
    const y = isTall ? (targetElRect.top + 2 * (targetElRect.height / 3)) : targetElRect.bottom;
    tooltip.style.position = 'fixed';
    tooltip.style.top = `${y}px`;
    tooltip.style.zIndex = '1000'; // TODO: Consider dropping to 100-199 range to adhere to z-index notes in app.css
    document.body.appendChild(tooltip);

    const tooltipRect = tooltip.getBoundingClientRect();
    tooltip.style.left = `${targetElCenterX - (tooltipRect.width / 2)}px`;
    let arrowX = (tooltipRect.width / 2); // calc carrot position inside tooltip
    tooltip.style.setProperty('--carrot-pos', `${arrowX}px`);
}

export function hideToolTip() {
    document.querySelector('#tooltip')?.remove();
}

document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggers = document.querySelectorAll('.tooltip');

    // Add listener to each tooltip
    tooltipTriggers.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltipText = element.getAttribute('data-tip');
            showToolTip(element, tooltipText);
        });
        element.addEventListener('mouseleave', () => {
            hideToolTip();
        });
    });
});