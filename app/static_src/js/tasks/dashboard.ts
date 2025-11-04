

export function init() {

    const isFrogCheckbox = document.querySelector<HTMLInputElement>('#is_frog');
    const dueDateField = document.querySelector<HTMLInputElement>('#due_date');
    if (!isFrogCheckbox || !dueDateField) return;

    isFrogCheckbox.addEventListener('change', () => {
        dueDateField.required = isFrogCheckbox.checked;
    });
}