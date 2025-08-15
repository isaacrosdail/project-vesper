// Utility, explicitly export & import where used

export function setupModal(modalId, buttonId, endpoint, successMsg) {
    const modal = document.querySelector(`#${modalId}`);
    if (!modal) return; // Exit if no modal on page

    document.addEventListener('click', (e) => {
        if (e.target.matches(`#${buttonId}`)) {
            modal.showModal();
        }
        else if (e.target.matches('#modal-close-btn')) {
            modal.querySelector('form').reset();
            modal.close();
        }
    });

    modal.addEventListener('cancel', () => {
        modal.querySelector('form')?.reset();
    });

    modal.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData // TODO: NOTES: No headers needed for formData obj
            });
            const responseData = await response.json();
            
            if (responseData.success) {
                if (successMsg && typeof makeToast === 'function') {
                    makeToast(successMsg);
                }
                modal.querySelector('form').reset();
                modal.close();
            } else {
                console.error('Error:', responseData.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

}