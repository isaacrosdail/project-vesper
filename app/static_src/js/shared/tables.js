// Bundler: Auto-runner => wires tables on DOMContentLoaded
import { makeToast } from './ui/toast.js';
import { apiRequest } from './services/api.js';

/**
 * Creates table row for given item data for realtime modal entries
 * @param {Object} item - Return data from backend for new item
 */
// TODO: Implement!
export function makeTableRow(item, subtype) {
    // const row = document.createElement("tr");
    // console.log("makeTableRow hit")
    // // Build cells
    // const template = document.querySelector(`#template-${subtype}`);
    // const clone = template.content.firstElementChild.cloneNode(true);
    // clone.dataset.itemId = item.id;
}


/**
 * Remove table row
 * @param {number} itemId - Item ID by which to query for row
 * @returns {void}
 */
export function removeTableRow(itemId) {
    const itemRow = document.querySelector(`[data-item-id="${itemId}"]`);
    if (!itemRow) return;

    const tableBody = itemRow.closest('tbody');
    itemRow.remove();

    // Insert "No items yet" placeholder text for table if removing last itemRow
    if (tableBody.children.length === 0) {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = 99;
        emptyCell.classList.add('table-empty');
        emptyCell.textContent = "No entries yet.";
        emptyRow.appendChild(emptyCell);
        tableBody.appendChild(emptyRow);
    }
}

/** 
 * Enables inline editing of a DOM element's text content via temporary input field.
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

    element.textContent = '';
    element.appendChild(input);
    input.focus();

    // Trigger save on blur or Enter key
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

document.addEventListener('dblclick', async (e) => {

    if (e.target.classList.contains('editable-cell')) {
        const td = e.target;
        const newValue = await inlineEditElement(td);
        if (newValue) {
            const { module, field, itemId, subtype } = td.dataset;
            const url = `/${module}/${subtype}/${itemId}`;

            apiRequest('PATCH', url, (responseData) => {
                makeToast(responseData.message, 'success');
            }, { [field]: newValue });
        }
    }
});