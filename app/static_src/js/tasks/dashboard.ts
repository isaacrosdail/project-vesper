
import { formatToUserTimeString } from "../shared/datetime";
import { initValidation, makeValidator } from '../shared/validators';
import { contextMenu } from '../shared/ui/context-menu';
import { confirmationManager, newHandleEdit, handleDelete } from '../shared/ui/modal-manager.js';


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
        dueDateField.required = isFrogCheckbox.checked;
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

    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;

        if (target.matches('.js-table-options')) {
            const button = target.closest('.row-actions')!;
            const modal = document.querySelector('#tasks-entry-dashboard-modal');
            const itemId = target.closest('.table-row')!.dataset.itemId;
            // const { itemId, module, subtype } = row.dataset;
            const url = `/tasks/tasks/${itemId}`;

            const rect = button.getBoundingClientRect();
            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => {
                            console.log("Editing task: ", itemId);
                            newHandleEdit(itemId, url, modal, 'Task');
                        }
                    },
                    {
                        label: 'Delete',
                        action: () => {
                            console.log("Deleting task: ", itemId);
                            handleDelete(itemId, url);
                        }
                    }
                ]
            })
        }
    });
}