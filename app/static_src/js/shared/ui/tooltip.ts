// Bundler => auto-runner
// Custom tooltip behavior

/**
 * To use for a given element:
 * - `.tooltip` for styling, `data-tip` for behavior
 * - Uses passed text if provided, otherwise falls back to `data-tip`
 * - Add 'data-tip' attr with desired tooltip text
 */
export function showTooltip(targetEl: HTMLElement | SVGElement, tooltipText?: string): void {
    const text = tooltipText || targetEl.getAttribute('data-tip');
    if (!text) {
        console.warn('No tooltip text provided');
        return;
    }

    const tooltip = document.createElement('div');
    tooltip.id = 'tooltip';
    tooltip.className = 'tooltip';
    tooltip.setAttribute('role', 'tooltip'); // For a11y
    tooltip.setAttribute('aria-hidden', 'false');
    targetEl.setAttribute('aria-describedby', tooltip.id); // Needs to be on trigger, not tooltip itself

    tooltip.textContent = text;

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
    const arrowX = (tooltipRect.width / 2); // calc carrot position inside tooltip
    tooltip.style.setProperty('--carrot-pos', `${arrowX}px`);
}

export function hideTooltip() {
    document.querySelector<HTMLElement>('#tooltip')?.remove();
}

document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggers = document.querySelectorAll<HTMLElement>('[data-tip]');

    // Add listener to each tooltip
    tooltipTriggers.forEach(element => {
        element.addEventListener('mouseenter', () => {
            const tooltipText = element.getAttribute('data-tip');
            if (!tooltipText) {
                console.warn('Tooltip element missing data-tip attribute: ', element);
                return;
            }
            showTooltip(element, tooltipText);
        });
        element.addEventListener('mouseleave', () => {
            hideTooltip();
        });
    });
});