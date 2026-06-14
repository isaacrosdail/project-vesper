
// Define the type alias
type ToastType = 'info' | 'success' | 'error' | 'warning';

class Toast {
    message: string;
    type: ToastType;
    element: HTMLElement | null;
    duration: number;

    constructor(message: string, duration: number, type: ToastType = 'info') {
        this.message = message;
        this.type = type;
        this.element = null;
        this.duration = duration
    }

    createElement(): HTMLElement {
        this.element = document.createElement('div');
        this.element.classList.add('toast', `toast-${this.type}`);

        const msg = document.createElement('span');
        msg.textContent = this.message;

        const dismissBtn = document.createElement('button');
        dismissBtn.classList.add('toast-dismiss');
        dismissBtn.innerHTML = '<svg class="icon"><use href="#icon-x"></use></svg>'
        dismissBtn.addEventListener('click', () => this.hide());

        this.element.append(msg, dismissBtn);
        this.element.style.setProperty('--toast-duration', `${this.duration}ms`)
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
        return this;
    }

    // Handle hiding/tidying up
    hide(): Toast {
        if (this.element) {
            this.element.classList.add('toast-exit');
            this.element.addEventListener('animationend', () => {
                this.element?.remove();
                this.element = null;
            }, { once: true });
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
export function makeToast(message: string, type: ToastType = 'info', duration: number = 2000): Toast {
    const toast = new Toast(message, duration, type).show();
    setTimeout(() => toast.hide(), duration); // auto-hide/fade
    return toast; // so the caller can do something with it if desired
}