
import { formatToUserTimeString } from '../shared/datetime';
import { initProductForm, initTransactionForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { userStore } from '../shared/services/userStore';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager';
import { makeToast } from '../shared/ui/toast';
import { title } from '../shared/utils';
import { FormDialog, Product, Transaction } from '../types';


let defaultTable;
let defaultTimeframe;

type TableOption = 'products' | 'transactions';
let selected: TableOption = defaultTable || 'products';

type TableCache = {
    products: Product[];
    transactions: Transaction[];
}
let cache: TableCache = { products: [], transactions: [] };

type SortOrder = 'asc' | 'desc' | '';
let currentSort: { key: string, order: SortOrder } = { key: '', order: '' };

type ColumnConfig = {
    label: string; // technically should prob be of type SORT_LABELS or something?
    key: string; // field name on the data
    format?: (value: any, row: any) => string; // optional function taking a val and rets a string
}


function initForms() {
    const productFormDialog = document.querySelector<FormDialog>('#products-entry-dashboard-modal')
    if (!productFormDialog) {
        console.warn('groceries dashboard: #products-entry-dashboard-modal not found')
        return
    }
    initProductForm(productFormDialog)

    const transactionFormDialog = document.querySelector<FormDialog>('#transactions-entry-dashboard-modal')
    if (!transactionFormDialog) {
        console.warn('groceries dashboard: #transactions-entry-dashboard-modal not found')
        return
    }
    initTransactionForm(transactionFormDialog)
}

function loadDefaults() {
    const prefs = userStore.data.preferences || {};
    selected = prefs.default_table || 'products';
    defaultTimeframe = Number(prefs.default_timeframe) || 30;
}

function initContextMenu(table: HTMLTableElement) {
    table.addEventListener('contextmenu', (e: MouseEvent) => {
        e.preventDefault();
        const row = e.target.closest('tr');
        if (!row) return;
        const id = row.dataset.id;
        if (!id) {
            console.warn('table contextmenu: missing ID for row');
            return
        };
        // selected = which table, id = which row, cache[selected] = all data
        const modal = document.querySelector(`#${selected}-entry-dashboard-modal`);
        const items = [
            {
                label: 'Edit',
                action: () => {
                    if (selected === 'transactions') {
                        openModalForEdit(id, modal, selected, (data) => {
                            const productSelectInput = modal.querySelector<HTMLSelectElement>('#product_id');
                            const productInputHidden = modal.querySelector<HTMLInputElement>('#product_id_hidden');
                            if (productSelectInput && productInputHidden) {
                                productSelectInput.dataset['originalInnerHTML'] = productSelectInput.innerHTML;
                                productSelectInput.innerHTML = `<option selected>${data.product_name}</option>`;
                                productSelectInput.disabled = true;
                                productInputHidden.value = data.product_id;
                                productInputHidden.disabled = false; // enable for edit, starts out disabled
                            }
                        });
                    } else {
                        openModalForEdit(id, modal, selected);
                    }
                }
            },
            { label: 'Delete', action: () => handleDelete(id, selected) },
        ];

        if (selected === 'products') {
            items.push({
                label: 'Add to Shopping List',
                action: () => api.shopping_list.addItem(id)
            });
        } else if (selected === 'transactions') {
            const item = cache.transactions.find(t => String(t.id) === id); // TODO: change to a map
            if (item) {
                items.push({
                    label: 'Add to Shopping List',
                    action: () => api.shopping_list.addItem(item.id)
                });
            }
        }

        contextMenu.create({
            position: { x: e.clientX, y: e.clientY },
            items: items,
        });
    })
}

const chevronSVG = `<svg class="sort-chevron"><use href="#icon-chevron"></use></svg>`;

const configs: Record<TableOption, { cols: ColumnConfig[] }> = {
    products: {
        cols: [
            { label: 'Name', key: 'name' },
            { label: 'Category', key: 'category', format: (v) => `${title(v.replace('_', ' & '))}`},
            { label: 'Net Weight', key: 'net_weight', format: (v, row) => `${v} (${row.unit_type})`},
            { label: 'Calories', key: 'calories' },
        ]
    },
    transactions: {
        cols: [
            { label: 'Product', key: 'product_name'},
            { label: 'Price', key: 'price_at_scan', format: (v) => `$${v.toFixed(2)}`},
            { label: 'Price/100g', key: 'price_per_100g', format: (v) => `$${v.toFixed(2)}`},
            { label: 'Date', key: 'created_at', format: (v) => formatToUserTimeString(new Date(v), { month: 'short', day: 'numeric'}) },
        ]
    }
};

function sortData<T>(data: T[], key: keyof T, order: SortOrder): T[] {
    return [...data].toSorted((a, b) => {
        if (order === 'desc') return a[key] > b[key] ? 1 : -1;
        return a[key] < b[key] ? 1 : -1;
    });
};

function setupSorting(table: HTMLTableElement) {
    table.addEventListener('click', (e) => {
        const sortHeader = e.target as HTMLTableCellElement;
        if (sortHeader.closest('th[data-sortable]')) {
            const th = sortHeader.closest<HTMLTableCellElement>('th[data-sortable]'); // would this even be null? How'd we "get here" if it was?
            const key = th.dataset.column;
            const order = th.dataset.order;
            const newOrder = order === 'asc' ? 'desc' : 'asc';
            currentSort.order = newOrder;
            currentSort.key = key;
            const sorted = sortData(cache[selected], key, newOrder);
            table.querySelectorAll('th').forEach(th => th.dataset.order = '') // clear old orders?
            th.dataset.order = newOrder; //set active
            renderTbody(configs[selected], sorted); // re-render body only
        }
    });
}

function buildHeader(col: ColumnConfig): string {
    const order = currentSort.key === col.key ? currentSort.order : '';
    return `<th data-column="${col.key}" data-sortable data-order="${order}">
        <span class="sort-label">${col.label}${chevronSVG}</span>
        </th>`;
}

function renderTable(config: { cols: ColumnConfig[] }, data: Record<string, unknown>) {
    const thead = document.querySelector('thead');
    thead.innerHTML = `<tr>${config.cols.map(buildHeader).join('')}</tr>`;
    renderTbody(config, data);
}

function renderTbody(config: { cols: ColumnConfig[] }, data: Record<string, unknown>) {
    const tbody = document.querySelector('tbody');
    tbody.innerHTML = data.map(row => `<tr data-id="${row.id}">${config.cols.map(c => {
        const text = c.format ? c.format(row[c.key], row) : row[c.key] ?? '';
        return `<td>${text}</td>`
    }).join('')}</tr>`).join('');
}

export async function init() {
    loadDefaults();
    console.log(`Default table read in as: ${selected}`)

    // Fetch & cache
    const [productData, transactionData] = await Promise.all(
        [api.products.getAll(), api.transactions.getAll()]
    );
    cache.products = productData.data;
    cache.transactions = transactionData.data;

    renderTable(configs[selected], cache[selected])
    // Set default table's btn to active
    document.querySelector(`[data-table="${selected}"]`)?.classList.add('active');

    const table = document.querySelector<HTMLTableElement>('#my-table');
    if (!table) throw new Error('Missing table #my-table')
    setupSorting(table);
    initContextMenu(table);

    // For our table select options, make right-click add an option for "Set as default table"
    const tableBtns = document.querySelectorAll('.table-select button');
    console.log(`Found ${tableBtns.length} table btns`)
    tableBtns.forEach(btn => {
        btn.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            contextMenu.create({
                position: { x: e.clientX, y: e.clientY },
                items: [
                    { label: 'Set as default', action: () => {
                        api.preferences.patch({ default_table: btn.dataset.table });
                        makeToast('Default table updated', 'success')
                    }}
                ]
            })
        })
    })


    // Then in our sidebar, we'll make buttons for each item "Product", "Transaction", etc, and switch based on that:
    // const sidebar = document.querySelector('.data-sidebar');
    const tableSelect = document.querySelector('.table-select');
    tableSelect.addEventListener('click', (e) => {
        const target = (e.target as HTMLElement).closest('[data-table]');
        if (!target) return;
        // if table-{thing} is in the config for tables -> swap to that choice/table?
        selected = e.target.dataset.table as TableOption;
        if (selected in configs) {
            // toggle active class
            tableSelect.querySelectorAll('[data-table]').forEach(el => el.classList.remove('active'));
            target.classList.add('active');
            renderTable(configs[selected], cache[selected]);
        };
    })

    initForms(); // init forms

    // // 3. Timeframe for tables
    // const timeframeInput = document.querySelector('#default-timeframe');
    // timeframeInput.addEventListener('change', (e) => {
    //     defaultTimeframe = e.target.value;
    //     api.preferences.patch({ default_timeframe: defaultTimeframe })
    // })

}


// TODO: Scraps, purge after we're done here

// function setEditMode(editing: boolean) {
//     document.querySelector('.edit-btn').classList.toggle('hide', editing);
//     document.querySelector('.save-btn').classList.toggle('hide', !editing);
//     document.querySelector('.cancel-btn').classList.toggle('hide', !editing);
// }
// const getValueSpans = (root: HTMLElement) => root.querySelectorAll('.target-value');

// function onEdit(root: HTMLElement) {
//     setEditMode(true);
//     getValueSpans(root).forEach(span => swapToInput(span));
// }
// function onSave(root: HTMLElement) {
//     const spans = getValueSpans(root);
//     const inputs = root.querySelectorAll('input');

//     inputs.forEach((input, i) => {
//         swapToText(spans[i], input.value);
//         defaultTargets[spans[i].dataset.target] = input.value;
//     });

//     setEditMode(false);
//     api.preferences.patch(defaultTargets);
// }

// function onCancel(root) {
//     root.querySelectorAll('input').forEach(input => {
//         const span = input.closest('.targetValue');
//         span.textContent = input.dataset.original;
//     });
//     setEditMode(false);
// }

// const goalsSection = sidebar.querySelector('.goals');
// goalsSection.addEventListener('click', (e) => {
//     const target = e.target;

//     if (target.matches('.edit-btn')) return onEdit(goalsSection);
//     if (target.matches('.save-btn')) return onSave(goalsSection);
//     if (target.matches('.cancel-btn')) return onCancel(goalsSection);
// });