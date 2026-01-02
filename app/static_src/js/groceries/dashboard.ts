// Entry point for groceries JS
import { confirmationManager } from '../shared/ui/modal-manager.js';
import { apiRequest } from '../shared/services/api.js';

type UnitGroupKey = 'weight' | 'volume';
type Unit = 'g' | 'kg' | 'oz' | 'lb' | 'ml' | 'l' | 'fl_oz';

const unitGroups: Record<UnitGroupKey, Unit[]> = {
    weight: ['g', 'kg', 'oz', 'lb'],
    volume: ['ml', 'l', 'fl_oz']
}

type UnitOptionsMap = Record<string, UnitGroupKey[]>;
// Map categories to groups: keys are categories, values are groups (in turn, keys for above dict)
const unitOptionsMap: UnitOptionsMap = {
    beverages: ["volume"],
    condiments_sauces: ["volume"],
    fruits: ["weight"],
    vegetables: ["weight"], 
    legumes: ["weight"],
    grains: ["weight"],
    bakery: ["weight"],
    meats: ["weight"],
    seafood: ["weight"],
    snacks: ["weight"],
    sweets: ["weight"],
    processed_convenience: ["weight", "volume"],
    supplements: ["weight", "volume"],
    dairy_eggs: ["weight", "volume"],
    fats_oils: ["weight", "volume"],
}

/**
 * Handles click actions (inc/dec, delete) on shopping list items.
 * Dispatches to appropriate API call and updates the DOM onSuccess accordingly.
 * 
 * @param targetEl - Target HTMLElement from click event.
 */
async function handleListActionClick(targetEl: HTMLElement): Promise<void> {
    const action = targetEl.dataset['action'];
    if (!action) return;

    const item = targetEl.closest('.shoppinglist-item');
    if (!(item instanceof HTMLElement)) return;
    const itemId = item.dataset['itemId'];
    const url = `/groceries/shopping_list_items/${itemId}`;

    switch(action) {
        case "delete": {
            const confirmed = await confirmationManager.show(
                    "Are you sure you want to delete this item?"
            );
            if (!confirmed) return;

            apiRequest('DELETE', url, null, {
                onSuccess: () => {
                    item.remove();
                }
            });
            return;
        }

        case "increment":
        case "decrement": {
            const currentQuantity = parseInt(
                item.dataset['quantityWanted'] ?? '0',
                10
            );
            if (isNaN(currentQuantity)) return;

            const container = targetEl.closest<HTMLElement>('.qty-controls');
            const qtySpan = container?.querySelector<HTMLSpanElement>('.item-qty');

            const qtyChange = action === 'increment' ? 1 : -1;
            const newQtyNum = currentQuantity + qtyChange;
            const newQty = String(newQtyNum);

            if (action === 'decrement' && newQtyNum === 0) {
                const confirmed = await confirmationManager.show(
                    "Are you sure you want to delete this item?"
                );
                if (!confirmed) return;

                apiRequest('DELETE', url, null, {
                    onSuccess: () => {
                        item.remove();
                    }
                });
                return;
            }

            const btn = targetEl as HTMLButtonElement;
            btn.disabled = true;

            apiRequest('PATCH', url, { quantity_wanted: newQty }, {
                onSuccess: () => {
                    qtySpan.textContent = newQty;
                    item.dataset['quantityWanted'] = newQty;
                    btn.disabled = false;
                }
            });
            break;

        }
    }
}

/**
 * Filters available unit options in product/transaction form modals
 * based on selected category (eg, hides ml/l for "Bakery")
 * @param {Event} e Change event from a category <select>
 */
function handleUnitFiltering(e: Event): void {
    if (!(e.target instanceof HTMLSelectElement)) return;
    const form = e.target.closest('form');
    if (!form) return;

    const categoryElement = form.querySelector<HTMLSelectElement>('[name="category"]');
    const unitSelect = form.querySelector<HTMLSelectElement>('[name="unit_type"]');
    if (!categoryElement || !unitSelect) return;

    const categorySelection = categoryElement.value;
    const unitTypes = unitSelect.querySelectorAll('option');

    // 2-step lookup with dict keys to store appropriate list of allowed units for given selection in allowedUnits
    // const allowedUnits = unitGroups[unitOptionsMap[categorySelection]];
    const groupKeys = unitOptionsMap[categorySelection];
    if (!groupKeys) return;

    const allowedUnits = groupKeys.flatMap(key => unitGroups[key]);

    const currentUnitsSelected = unitSelect.value as Unit;
    if (!allowedUnits.includes(currentUnitsSelected)) {
        unitSelect.value = '';
    }

    unitTypes.forEach(option => {
        option.hidden = !allowedUnits.includes(option.value as Unit);
    });
}

function toggleProductFields(e: Event): void {
    if (!(e.target instanceof HTMLSelectElement)) return;

    const form = e.target.closest('form')!;
    const productFields = form.querySelectorAll('.product-field input, .product-field select');
    const isNew = (e.target.value === '__new__');

    productFields.forEach(field => {
        const htmlField = field as HTMLInputElement | HTMLSelectElement;
        htmlField.parentElement!.hidden = !isNew;
        htmlField.disabled = !isNew;

        if (!isNew) {
            htmlField.value = '';
        }
    })
}


export function init() {
    const transactionModal = document.querySelector<HTMLDialogElement>('#transactions-entry-dashboard-modal');
    const priceField = transactionModal?.querySelector<HTMLInputElement>('[name="price_at_scan"]');
    const shoppingList = document.querySelector('.shopping-list');
    if (!transactionModal || !priceField || !shoppingList) return;

    shoppingList.addEventListener('click', (e) => {
        if (!(e.target instanceof HTMLElement)) return;
        handleListActionClick(e.target);
    });

    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        
        if (target.matches('.table-range')) {
            const range = target.dataset['range']!;
            const table = target.dataset['table']!;

            const url = new URL(window.location.href);
            url.searchParams.set(`${table}_range`, range);
            window.location.href = url.toString();
        }
    });

    document.addEventListener('change', (e) => {
        const target = e.target;
        if (!(target instanceof HTMLElement)) return;

        if (target.matches('[name="category"]')) {
            handleUnitFiltering(e);
        }
        else if (target.matches('[name="product_id"]')) {
            toggleProductFields(e);
        }
    });

    transactionModal.addEventListener('close', () => {
        const productFields = transactionModal.querySelectorAll<HTMLInputElement | HTMLSelectElement>(
            '.product-field input, .product-field select'
        );
        productFields.forEach(el => {
            el.parentElement!.hidden = true;
            el.disabled = true;
        });
    })

    priceField.addEventListener('keydown', (e: Event) => {
        if (!(e instanceof KeyboardEvent)) return;

        const isDigit = /^\d$/.test(e.key); // digit 0-9

        if (isDigit) {
            e.preventDefault();

            const num = Math.round(Number(priceField.value) * 100);
            const combined = String(num) + e.key;
            const nextValue = (Number(combined) / 100);

            priceField.value = nextValue.toFixed(2);
        } else if (e.key === 'Backspace') {
            e.preventDefault();

            const currentDigit = Math.round(Number(priceField.value) * 100);
            const thing = Math.floor(currentDigit / 10);
            const nextValue = thing === 0 ? 0 : thing / 100;

            priceField.value = nextValue.toFixed(2);
        }
    })

    priceField.addEventListener('paste', (e) => {
        e.preventDefault();
        const pasted = e.clipboardData?.getData('text') ?? "";
        const currentCents = Math.round(Number(priceField.value) * 100);
        const nextCentsString = String(currentCents) + pasted;
        const nextValue = Number(nextCentsString) / 100;

        priceField.value = nextValue.toFixed(2);
    })
}
