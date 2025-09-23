import { confirmationManager } from './shared/ui/modal-manager.js';
import { makeToast } from './shared/ui/toast.js';
import { initPasswordToggles } from './shared/forms.js';

export function init() {
    initPasswordToggles();

    document.addEventListener('click', (e) => {
        if (e.target.matches('#default')) {
            confirmationManager.show("Are you sure?");
        }
        else if (e.target.matches('#toast-success')) {
            makeToast('SUCCESS', 'success');
        }
        else if (e.target.matches('#toast-error')) {
            makeToast('ERROR', 'error')
        }
    });
}