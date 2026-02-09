
import { formatToUserTimeString, getJSInstant } from "../shared/datetime";
import { apiRequest } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager.js';
import { makeToast } from '../shared/ui/toast';
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


function toggleTaskComplete(
    itemId: string,
    isDone: boolean
) {
    const newIsDone = !isDone;
    const completedAtUTC = getJSInstant();

    const data = {
        is_done: newIsDone,
        completed_at: completedAtUTC
    }
    const url = `/tasks/tasks/${itemId}`;

    apiRequest('PATCH', url, data, {
        onSuccess: () => {
            const row = document.querySelector<HTMLElement>(`[data-item-id="${itemId}"]`);
            if (!row) return;
            const statusSpan = row.querySelector('.status-span');

            if (newIsDone) {
                row.dataset['isDone'] = 'True';
            } else {
                delete row.dataset['isDone'];
            }
            statusSpan?.classList.toggle('is-done');

            makeToast('Task status updated', 'success')
        }
    });
}

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

    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;

        if (target.matches('.js-table-options')) {
            const button = target.closest('.row-actions')!;
            const row = target.closest('.table-row')!;
            const { itemId } = row.dataset;
            const url = `/tasks/tasks/${itemId}`;
            const modal = document.querySelector('#tasks-entry-dashboard-modal');
            const rect = button.getBoundingClientRect();

            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => openModalForEdit(itemId, url, modal, 'Task')
                    },
                    {
                        label: 'Delete',
                        action: () => handleDelete(itemId, url)
                    },
                    {
                        label: 'Toggle task complete',
                        action: () => {
                            const isDone = row.dataset.isDone === 'True';
                            toggleTaskComplete(itemId, isDone);
                        }
                    }
                ]
            })
        }
    });
}