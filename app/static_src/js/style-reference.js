import { confirmationManager } from './shared/ui/modal-manager.js';
import { makeToast } from './shared/ui/toast.js';

export function init() {
    if (!document.querySelector('#style-reference-root')) return;

    document.addEventListener('click', (e) => {
        if (e.target.matches('#default')) {
            confirmationManager.show("Are you sure?");
        }
        else if (e.target.matches('#alt')) {
            confirmationManager.show("Do you want a cookie?");
        }
        else if (e.target.matches('#toast-success')) {
            makeToast('SUCCESS', 'success');
        }
        else if (e.target.matches('#toast-error')) {
            makeToast('ERROR', 'error')
        }
    });
}