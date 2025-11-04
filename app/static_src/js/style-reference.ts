import { confirmationManager } from './shared/ui/modal-manager.js';
import { makeToast } from './shared/ui/toast.js';
import { initPasswordToggles } from './shared/forms.js';

export function init() {
    initPasswordToggles();

    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('#default')) {
            confirmationManager.show("Are you sure?");
        }
        else if (target.matches('#toast-success')) {
            makeToast('SUCCESS', 'success');
        }
        else if (target.matches('#toast-error')) {
            makeToast('ERROR', 'error')
        }
    });
}