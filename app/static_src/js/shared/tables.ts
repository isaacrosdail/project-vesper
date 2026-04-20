// Bundler: Auto-runner => wires tables on DOMContentLoaded
import { api } from './services/api';
import { makeToast } from './ui/toast';
import { ENUM_SORT_ORDERS } from '../types';


/**
 * Remove a table row from the DOM and insert placeholder text if table is now empty.
 * 
 * @param itemId - Item ID used to query for the row via [data-item-id] attribute
 */
export function removeTableRow(itemRow: HTMLElement): void {
    const tableBody = itemRow.closest('tbody');
    itemRow.remove();

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

// Cache table sort
type SortState = { field: string; order: 'asc' | 'desc' } | undefined;
const tableSorts = new Map<string, SortState>();

const tableRanges = new Map<string, number>(); // Track table range: subtype -> current range

function sortByField<T>(items: T[], field: keyof T, order: 'asc' | 'desc'): T[] {
    const customOrder = ENUM_SORT_ORDERS[field as string];

    return items.toSorted((a, b) => {
        const valA = a[field]
        const valB = b[field]

        // Sort nulls last
        if (valA === null && valB === null) return 0;
        if (valA === null) return 1;
        if (valB === null) return -1;

        const result = customOrder
            ? customOrder[valA as string] - customOrder[valB as string]
            : typeof valA === 'string'
                ? valA.localeCompare(valB as string)
                : (valA as number) - (valB as number);
        return order === 'asc' ? result : -result; // localeCompare returns -1/1/0 too, so we can use -result to flip order!! :D
    })
}

/**
 * Handle client-side table sorting and range filtering via click events.
 */
document.addEventListener('click', async (e) => {
    const target = e.target as HTMLElement;
    // TODO: other stuff:
    // 1. Make it a no-op if new sorted would be identical to currently sorted OR if all fields are null anyway
    // ALSO: Get this to treat null fields together cleanly like the python version did
    if (target.closest('th[data-sortable]')) {
        // TODO: Hacky patch, fix this up
        const html = document.querySelector('html');
        if (html.dataset.page === 'groceries.data') return;
        const table = target.closest('table')!;
        const th = target.closest('th')!;
        const tbody = table.querySelector('tbody')!;
        const sortField = th.dataset.column;
        const { module, subtype } = table.dataset;

        // Fetch all, since 0 will eval to Falsy (hacky, prob need to improve later)
        const params = new URLSearchParams({ lastNDays: '0' })
        const { data } = await api[subtype].getAll();

        // Sort
        const current = tableSorts.get(subtype)
        const newOrder = (current?.field === sortField && current?.order === 'asc')
            ? 'desc'
            : 'asc';
        tableSorts.set(subtype, { field: sortField, order: newOrder })

        // Clear prev chevron
        const prevTh = table.querySelector('th[data-order]')
        if (prevTh) prevTh.removeAttribute('data-order')
        th.dataset.order = newOrder; // for CSS chevron flip

        const sortedItems = sortByField(data, sortField, newOrder)
        sortedItems.forEach(item => {
            const row = tbody.querySelector(`tr[data-item-id="${item.id}"]`)
            if (!row) {
                console.warn(`tables sort: no row for id ${item.id}`)
                return
            }
            tbody.append(row) // move to new pos
        })
    }
    else if (target.matches('.table-range')) {
        const card = target.closest<HTMLDivElement>('.card-dashboard')!
        const table = card.querySelector('table')!
        const tbody = table.querySelector('tbody')!
        const { module, subtype } = table.dataset;

        const newRange = target.dataset.range!; // set new range to what we just clicked
        tableRanges.set(subtype, Number(newRange));

        const params = new URLSearchParams({ lastNDays: newRange })
        const { data } = await api[subtype].getAll(params);

        // Show/hide rows based on what returned - match IDs to do "show those with ID in response.data"
        const visibleIds = new Set(data.map(item => String(item.id)));
        tbody.querySelectorAll('tr').forEach(row => {
            row.classList.toggle('hide', !visibleIds.has(row.dataset.itemId))
        })
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
        const response = await api[subtype].patch(itemId, { [field]: newValue });
        makeToast(response.message, 'success');
    }
});