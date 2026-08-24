// Custom tooltip behavior

import { required } from "../dom";

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

const tooltip = required(document.querySelector<HTMLElement>('#tooltip'), '#tooltip');

export function createTooltip(targetEl: HTMLElement | SVGElement, tooltipText?: string): void {
    const text = tooltipText || targetEl.getAttribute('data-tip');
    if (!text) {
        console.warn('No tooltip text provided');
        return;
    }
    // targetEl.style.anchorName = '--tooltip-anchor';
    targetEl.style.setProperty('anchor-name', '--tooltip-anchor')
    tooltip.textContent = text;
    targetEl.setAttribute('aria-describedby', 'tooltip');
    tooltip.showPopover();
}

export function removeTooltip(targetEl: HTMLElement | SVGElement) {
    targetEl.style.setProperty('anchor-name', '');
    tooltip.hidePopover();
}

/** Svelte action: <button use:tip={'Delete habit'}> */
export function tip(node: HTMLElement, text: string) {
    const enter = () => createTooltip(node, text);
    const leave = () => removeTooltip(node);
    node.addEventListener('mouseenter', enter);
    node.addEventListener('mouseleave', leave);
    return {
        update(newText: string) {
            text = newText;
        },
        destroy() {
            node.removeEventListener('mouseenter', enter);
            node.removeEventListener('mouseleave', leave);
            removeTooltip(node);
        },
    };
}