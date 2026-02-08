// Utilities to leverage TS' type narrowing efficiently

export function isCheckbox(el: Element | null): el is HTMLInputElement & { type: 'checkbox' } {
    return el instanceof HTMLInputElement && el.type === 'checkbox';
}