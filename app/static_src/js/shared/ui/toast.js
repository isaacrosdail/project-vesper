// Bundler: Auto-runner (listener) + utility (makeToast)
// Import + export makeToast() explicitly where needed

// Build DOM node for toast element with specified traits/properties
// Receives message, then decides _how_ to display it only
export function makeToast(myMsg) {
    // Make toast element
    const toast = document.createElement('div');
    toast.classList.add('toast-message');
    // STYLE: NOTE: Using setAttr for consistency even though toast.id = ''; is more idiomatic
    toast.setAttribute('id', 'toast-message');
    toast.textContent = myMsg;
    document.body.appendChild(toast);
}

// Event listener for fade out
window.addEventListener('DOMContentLoaded', () => {
    const toast = document.querySelector('#flash-message');
    if (toast) {
        setTimeout(() => {
            toast.style.opacity = '0'; // fade?
            toast.style.pointerEvents = 'none'; // ?
            setTimeout(() => toast.remove(), 1000); // then remove after fade
        }, 2000);
    }
});