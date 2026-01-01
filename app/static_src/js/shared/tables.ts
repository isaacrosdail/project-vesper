// Bundler: Auto-runner => wires tables on DOMContentLoaded
import { makeToast } from './ui/toast.js';
import { apiRequest } from './services/api.js';


/**
 * Remove a table row from the DOM and insert placeholder text if table is now empty.
 * 
 * @param itemId - Item ID used to query for the row via [data-item-id] attribute
 */
export function removeTableRow(itemRow: HTMLElement): void {
    const tableBody = itemRow.closest('tbody');
    itemRow.remove();

    // Insert "No items yet" placeholder if removing last itemRow
    if (tableBody && tableBody.children.length === 0) {
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
 * Convert a text element into an inline-editable input field temporarily.
 * User can edit & save via Enter key or blur event.
 * 
 * @param element - Target element containing text to edit (eg, <td>, <span>)
 * @returns Promise resolving to new value if changed, null if unchanged or undefined
 */
export async function inlineEditElement(element: HTMLElement): Promise<string|null> {
    const originalText = element.textContent?.trim() ?? '';

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

/**
 * Handle table header clicks for column sorting.
 * Updates URL parameters & reloads page with new sort order.
 */
document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;

    if (target.matches('.sort-header')) {
        const table = target.closest('table');
        const subtype = table?.dataset['subtype'];
        const th = target.closest('th')!;
        const field = th.dataset['column'];
        const oldSortOrder = th.dataset['order'];

        const sortOrder = (oldSortOrder === 'asc') ? 'desc' : 'asc';

        const url = new URL(window.location.href);
        url.searchParams.set(`${subtype}_sort`, `${field}`);
        url.searchParams.set(`${subtype}_order`, sortOrder);
        window.location.href = url.toString();
    }
});

/**
 * Handle double-click on elements with .editable-cell class
 * 
 * Requires data attributes on parent <td>:
 * - data-module: Resource module (eg, groceries)
 * - data-subtype: Resource type (eg, products, transactions, etc)
 * - data-item-id: Item/resource identifier
 * - data-field: Field name to update
 */
document.addEventListener('dblclick', async (e) => {
    if (!(e.target instanceof HTMLElement)) return;

    if (e.target.classList.contains('editable-cell')) {
        let td: HTMLTableCellElement;
        if (e.target instanceof HTMLTableCellElement) {
            td = e.target;
        } else { //(e.target instanceof HTMLSpanElement)
            const foundTd = e.target.closest('td');
            if (!foundTd) {
                console.error('editable-cell must be a <td> or inside a <td>');
                return;
            }
            td = foundTd as HTMLTableCellElement;
        }

        const newValue = await inlineEditElement(e.target);
        if (!newValue) return;

        const { module, field, itemId, subtype } = td.dataset;
        if (!module || !field || !itemId || !subtype) {
            console.error('Missing data attribute');
            return;
        }
        const url = `/${module}/${subtype}/${itemId}`;

        apiRequest('PATCH', url, (responseData: { message: string }) => {
            makeToast(responseData.message, 'success');
        }, { [field]: newValue });
    
    }
});