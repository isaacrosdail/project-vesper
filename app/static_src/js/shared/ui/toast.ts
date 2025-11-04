
// Define the type alias
type ToastType = 'info' | 'success' | 'error' | 'warning';

class Toast {
    message: string;
    type: ToastType;
    element: HTMLElement | null;

    constructor(message: string, type: ToastType = 'info') {
        this.message = message;
        this.type = type;
        this.element = null;
    }

    createElement(): HTMLElement {
        this.element = document.createElement('div');
        this.element.classList.add('toast', `toast-${this.type}`);
        this.element.textContent = this.message;
        return this.element;
    }

    // Create + add to DOM
    show(): Toast {
        if (!this.element) {
            this.createElement();
        }

        const container = document.querySelector('#toast-container');
        if (!container) {
            throw new Error('Toast container not found in DOM');
        }
        container.appendChild(this.element!);
        return this; // for chaining?
    }

    // Handle hiding/tidying up
    hide(): Toast {
        if (this.element) {
            this.element.remove();
            this.element = null;
        }
        return this;
    }
}

/**
 * Creates and displays a toast notification with auto-hide.
 * 
 * @example
 * makeToast("Saved successfully", "success", 2000);
 * 
 * // Or handle manually:
 * const toast = makeToast("Working..", "info", 0);
 * setTimeout(() => toast.hide(), 5000);
 */
export function makeToast(message: string, type: ToastType = 'info', duration: number = 1000): Toast {
    const toast = new Toast(message, type).show();
    setTimeout(() => toast.hide(), duration); // auto-hide/fade
    return toast; // so the caller can do something with it if desired
}