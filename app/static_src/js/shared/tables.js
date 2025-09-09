// Bundler: Auto-runner => wires tables on DOMContentLoaded
// Functions for our tables, such as editTableField or deleteTableItem?
import { confirmationManager } from './ui/modal-manager.js';
import { makeToast } from './ui/toast.js';
import { apiRequest } from './services/api.js';

/**
 * Creates table row for given item data for realtime modal entries
 * @param {Object} data - Return data from backend for new item
 */
// TODO: Implement!
export function makeTableRow(data) {
    const row = document.createElement("tr");

    // Build cells

}


/**
 * Deletes item from DB when clicking delete button
 * @async
 * @param {string} module 
 * @param {number} itemId 
 * @param {string} subtype 
 * @returns 
 */
async function deleteTableItem(module, itemId, subtype = "none") {
    const confirmed = await confirmationManager.show("Are you sure you want to delete this item?");
    if (!confirmed) return;

    const url = `/${module}/${subtype}/${itemId}`;

    apiRequest('DELETE', url, () => {
        const itemRow = document.querySelector(`[data-item-id="${itemId}"]`);
        if (itemRow) itemRow.remove();
    });
}

/** 
 * Enables inline editing of a DOM element's text content via a temporary input field.
 * On blur or Enter key, input it replaced with text content.
 * Returns the new value if it was changed, or null if unchanged.
 * 
 * @param {HTMLElement} element - Target element to enable inline editing for.
 * @returns {Promise<string|null>} Resolves with the updated value, or null if unchanged.
 */
export async function inlineEditElement(element) {
    const originalText = element.textContent.trim();

    // Create input element with similar size to current text
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'input-inline';
    input.value = originalText;
    input.size = originalText.length + 2;

    // Clear element & append input
    element.textContent = '';
    element.appendChild(input);
    input.focus();

    // Trigger save on blur or Enter key
    // Note: Pressing Enter triggers a blur, so the change logic is centralized in handleFinish
    return new Promise((resolve) => {
        input.addEventListener('blur', handleFinish);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                input.blur(); // trigger blur => handleFinish => resolve
            }
        });

        function handleFinish() {
            const newValue = input.value.trim();
            element.textContent = newValue || originalText;
            resolve(newValue !== originalText ? newValue : null);
        }
    });
}

// 1. Get the value from the input field (represents our edited title)
// 2. Send it to the backend to update the task in the db
// 3. Once updated, replace the input with the new title and hide the input field
/** 
 * Updates item's corresponding field with new table cell's value.
 * @param {string} module - API module name 
 * @param {string} field - Field name being updated
 * @param {string|number} itemId - ID of item to update
 * @param {string} newValue - New field value
 * @param {HTMLElement} td - Table cell element to update
 */
async function saveUpdatedField(module, field, itemId, newValue, td, subtype = "none") {
    // Construct URL & request body
    const url = `/${module}/${subtype}/${itemId}`;
    const data = {}
    data[field] = newValue;

    apiRequest('PATCH', url, () => {
        makeToast(responseData.message, 'success');
    }, data);
}

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', (e) => {
        // Handle clicks on delete button or its contents (SVG)
        if (e.target.matches('.delete-btn') || e.target.closest('.delete-btn')) {
            const row = e.target.closest('tr');
            if (!row) return;
            deleteTableItem(row.dataset.module, row.dataset.itemId, row.dataset.subtype)
        }
    });
    document.addEventListener('dblclick', async (e) => {
        // Handle double-click to edit table cell
        if (e.target.classList.contains('editable-cell')) {
            const td = e.target;
            const newValue = await inlineEditElement(td);
            if (newValue) {
                await saveUpdatedField(td.dataset.module, td.dataset.field, td.dataset.itemId, newValue, td, td.dataset.subtype);
            }
        }
    });
});