// Bundler => auto-runner
// Custom tooltip behavior

/**
 * Create & display a tooltip anchored under a given element.
 * 
 * Caller is responsible for subsequently removing tooltip via `removeTooltip()`.
 * 
 * @param targetEl - Element to which to attach tooltip.
 * @param tooltipText - Tooltip text (falls back to `data-tip` attribute value if not provided)
 * 
 * @remarks
 * Styling via `.tooltip` class, behavior via `data-tip` attribute
 */
export function createTooltip(targetEl: HTMLElement | SVGElement, tooltipText?: string): void {
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
    targetEl.setAttribute('aria-describedby', tooltip.id); // Must be on trigger, not tooltip itself

    tooltip.textContent = text;

    const targetElRect = targetEl.getBoundingClientRect();
    const isTall = targetElRect.height > 80;
    const centerX = (targetElRect.left + targetElRect.right) / 2; // gives us dist from end to center for caret
    const y = isTall
        ? (targetElRect.top + 2 * (targetElRect.height / 3))
        : targetElRect.bottom;

    tooltip.style.zIndex = '1000';

    // Tooltips in dialogs need dialog parent to avoid stacking context issues
    const parentDialogEl = targetEl.closest('dialog');
    const isInDialog = parentDialogEl && parentDialogEl instanceof HTMLDialogElement;

    if (isInDialog) {
        parentDialogEl.appendChild(tooltip);
    } else {
        document.body.appendChild(tooltip);
    }

    const tooltipRect = tooltip.getBoundingClientRect(); // gives tooltips curr size and position 
    const tooltipCenterOffset = (tooltipRect.width / 2); // calc caret position inside tooltip

    if (isInDialog) {
        const dialogRect = parentDialogEl.getBoundingClientRect();
        
        tooltip.style.position = 'absolute';
        tooltip.style.top = `${y - dialogRect.top}px`;
        tooltip.style.left = `${centerX - dialogRect.left - tooltipCenterOffset}px`;

    } else {
        tooltip.style.position = 'fixed';
        tooltip.style.top = `${y}px`;
        const tooltipRectNew = tooltip.getBoundingClientRect(); // Must measure after position: fixed since element width changes when removed from document flow
        tooltip.style.left = `${centerX - (tooltipRectNew.width/2)}px`;
    }
    tooltip.style.setProperty('--caret-pos', '50%');
}

export function removeTooltip() {
    document.querySelector<HTMLElement>('#tooltip')?.remove();
}

document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggers = document.querySelectorAll<HTMLElement>('[data-tip]');

    // Add listener to each tooltip
    tooltipTriggers.forEach(el => {
        el.addEventListener('mouseenter', () => {
            const tooltipText = el.getAttribute('data-tip');
            if (!tooltipText) {
                console.warn('Tooltip element missing data-tip attribute: ', el);
                return;
            }
            createTooltip(el, tooltipText);
        });
        el.addEventListener('mouseleave', () => {
            removeTooltip();
        });
    });
});
