
import { formatToUserTimeString } from "../shared/datetime";
import { initValidation, makeValidator } from '../shared/validators';

function validateDueDate(dueDateString: string): string | null {
    const isFrogCheckBox = document.querySelector<HTMLInputElement>('#is_frog');
    const isFrog = isFrogCheckBox!.checked;

    // duedate exists -> check in future
    if (dueDateString) {
        // check in future
        const today = formatToUserTimeString(new Date(), {})
        const valid = today < dueDateString;
        return valid ? null : 'ERROR: Due date must be in the future';
    } else {
        return isFrog ? 'Due date required for frog tasks' : null;
    }
}

// Validators
const validateTaskName = makeValidator('name', {
    maxLength: 3,
});

// function validateSleepTimes() {
//     const blech = document.querySelector<HTMLInputElement>('#wake_datetime');
//     const blech2 = document.querySelector<HTMLInputElement>('#sleep_datetime');

//     // ensure sleep is after wake?

// }

export function init() {
    const isFrogCheckbox = document.querySelector<HTMLInputElement>('#is_frog');
    const dueDateField = document.querySelector<HTMLInputElement>('#due_date');
    const priorityField = document.querySelector<HTMLInputElement>('#priority');
    if (!isFrogCheckbox || !dueDateField) return;

    isFrogCheckbox.addEventListener('change', () => {
        // dueDateField.required = isFrogCheckbox.checked;
        priorityField.disabled = isFrogCheckbox.checked;
    });

    const form = document.querySelector<HTMLFormElement>('#tasks-form')!;
    // Validation
    initValidation(
    form,
        {
        due_date: validateDueDate,
        name: validateTaskName,
    })
}