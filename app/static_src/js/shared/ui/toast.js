
class Toast {
    constructor(message, type = 'info') {
        this.message = message;
        this.type = type;
        this.element = null;
    }

    createElement() {
        this.element = document.createElement('div');
        this.element.classList.add('toast', `toast-${this.type}`);
        this.element.textContent = this.message;
        return this.element;
    }

    // Create + add to DOM
    show() {
        if (!this.element) {
            this.createElement();
        }

        const container = document.querySelector('#toast-container');
        container.appendChild(this.element);
        return this; // for chaining?
    }

    // Handle hiding/tidying up
    hide() {
        if (this.element) {
            this.element.remove();
            this.element = null;
        }
        return this;
    }
}

/**
 * 
 * @param {string} message - The text to display inside the toast.
 * @param {string} type - Visual style variant of toast.
 * @param {number} duration - Time (in ms) before auto-hide.
 * @returns {Toast} - The Toast instance
 * 
 * @example
 * makeToast("Saved successfully", "success", 2000);
 * 
 * // Or handle manually:
 * const toast = makeToast("Working..", "info", 0);
 * setTimeout(() => toast.hide(), 5000);
 */
export function makeToast(message, type = 'info', duration = 1000) {
    const toast = new Toast(message, type).show();

    setTimeout(() => toast.hide(), duration); // auto-hide/fade

    return toast; // so the caller can do something with it if desired
}