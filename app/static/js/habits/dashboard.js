// Currently handles add habit modal

document.addEventListener('DOMContentLoaded', (e) => {
    const modal = document.querySelector('#add-habit-modal');
    // Event listener for modal click
    document.addEventListener('click', (e) => {
        if (e.target.matches('#add-habit-btn')) {
            modal?.showModal();
        }



        // TODO: Fix bug => Close causes "input field __ not focusable", doesn't seem to break functionality
        // just causes validation outline upon reopen
        else if (e.target.matches('#modal-close-btn')) {
            const form = modal.querySelector('form');
            form.reset();
            modal?.close();
        }
    });
    // Use native 'cancel' event for dialog to make Esc key close modal (a11y)
    modal.addEventListener('cancel', (e) => {
        modal.querySelector('form')?.reset();
    });
    // Listen for submit event on modal
    modal?.addEventListener('submit', (e) => {
        // e.target here is the form itself
        // The form fires the submit event which bubbles up to the modal where our listener catches it
        e.preventDefault(); // prevent default form submission behavior (Note: method on EVENT, not target)

        // Get our form data
        const formData = new FormData(e.target);
        saveModalFormSubmission(formData, e.currentTarget);

    });

    // testing
    modal?.addEventListener('close', (e) => {
        //if (modal.returnValue === 'save') saveStuff();
        form.reset();
        console.log(`Close triggered with value of: ${modal.returnValue}`);
    });
});

// Handle submission for modal
// Don't like passing modal, would rather isolate & handle .close
// in our event listener above, but that incurs rewrites I wouldn't
// like either
async function saveModalFormSubmission(formData, modal) {
    const url = '/habits';

    // POST fetch
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData // no headers needed for FormData object
        });

        // Reads our response body, parses it as JSON
        const responseData = await response.json();

        if (responseData.success) {
            const habit = responseData.habit;
            // Debug: console.log(`habit id: ${habit.title}`)
            modal.querySelector('form').reset(); // Clear form on submit
            modal?.close();
        } else {
            console.error('Error submitting Add Habit form:', responseData.message);
        }
    } catch (error) {
        console.error('Error during fetch request:', error);
    }
}