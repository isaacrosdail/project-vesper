
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
// Build DOM node for toast element with specified traits/properties
// Receives message, then decides _how_ to display it only
export function makeToast(message, type = 'info', duration = 1000) {
    const toast = new Toast(message, type).show();

    setTimeout(() => toast.hide(), duration); // auto-hide/fade

    return toast; // so the caller can do something with it if desired
}