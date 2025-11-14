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
     * Handles click actions (increment, decrement, delete) on shopping list items.
     * Dispatches to appropriate API call and updates the DOM onSuccess accordingly.
     * @param {*} e - Click event from listener
     * @returns 
     */
    async function handleListActionClick(e: Event): Promise<void> {
        if (!(e.target instanceof HTMLButtonElement)) return;
        const action = e.target.dataset['action'];
        if (!action) return;

        const item = e.target.closest('.shoppinglist-item') as HTMLElement;
        const itemId = item.dataset['itemId'];
        if (!item || !itemId) return;

        const currentQuantity = parseInt(item.dataset['quantityWanted'] ?? '0', 10);
        const container = e.target.closest('.qty-controls') as HTMLElement; // parent to subsequently grab span for qty to edit text
        const qtySpan = container?.querySelector('.item-qty') as HTMLElement; // then grab span for editing qty after fetches

        if (action === 'increment' || action === 'decrement') {
            if (!container || !qtySpan || isNaN(currentQuantity)) return;
        }

        const url = `/groceries/shopping_list_items/${itemId}`;


        switch(action) {
            case "increment": {
                const newQty = String(currentQuantity + 1);
                const incrementBtn = e.target;
                incrementBtn.disabled = true;
                apiRequest('PATCH', url, () => {
                    qtySpan.textContent = newQty;
                    item.dataset['quantityWanted'] = newQty;
                    incrementBtn.disabled = false;
                }, { quantity_wanted: newQty });
                break;
            }

            case "decrement": {
                const newQty = String(currentQuantity - 1);
                const decrementBtn = e.target;
                decrementBtn.disabled = true;

                if (newQty === "0") {
                    const confirmed = await confirmationManager.show("Are you sure? This will delete the item from your shopping list.");
                    if (!confirmed) {
                        decrementBtn.disabled = false;
                        return;
                    };
                    apiRequest('DELETE', url, () => item.remove());
                } else {
                    apiRequest('PATCH', url, () => {
                        // update DOM qty display
                        qtySpan.textContent = newQty;
                        item.dataset['quantityWanted'] = newQty;
                        decrementBtn.disabled = false;
                    }, { quantity_wanted: newQty });
                }
                break;
            }

            case "delete": {
                const confirmed = await confirmationManager.show("Are you sure you want to delete this item?");
                if (!confirmed) return;
                apiRequest('DELETE', url, () => item.remove());
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
        const form = e.target.closest('form') as HTMLFormElement;
        if (!form) return;

        const categoryElement = form.querySelector('[name="category"]') as HTMLSelectElement;
        const unitSelect = form.querySelector('[name="unit_type"]') as HTMLSelectElement;
        if (!categoryElement || !unitSelect) return;

        const categorySelection = categoryElement.value;
        const unitTypes = unitSelect.querySelectorAll('option');

        // 2-step lookup with dict keys to store appropriate list of allowed units for given selection in allowedUnits
        // const allowedUnits = unitGroups[unitOptionsMap[categorySelection]];
        const groupKeys = unitOptionsMap[categorySelection];
        if (!groupKeys) return;

        const allowedUnits = groupKeys.flatMap(key => unitGroups[key]);

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
    const transactionModal = document.querySelector('#transactions-entry-dashboard-modal');
    const priceField = transactionModal?.querySelector('[name="price_at_scan"]') as HTMLInputElement;
    const shoppingList = document.querySelector('.shopping-list');
    if (!transactionModal || !priceField || !shoppingList) return;

    shoppingList.addEventListener('click', handleListActionClick);

    document.addEventListener('change', (e) => {
        if (!(e.target instanceof HTMLElement)) return;

        if (e.target.matches('[name="category"]')) {
            handleUnitFiltering(e);
        }
        else if (e.target.matches('[name="product_id"]')) {
            toggleProductFields(e);
        }
    });

    transactionModal.addEventListener('close', () => {
        const productFields = transactionModal.querySelectorAll('.product-field input, .product-field select');
        productFields.forEach(field => {
            const htmlField = field as HTMLInputElement | HTMLSelectElement;
            htmlField.parentElement!.hidden = true;
            htmlField.disabled = true;
        })
    })

    priceField.addEventListener('keydown', (e: Event) => {
        if (!(e instanceof KeyboardEvent)) return;

        // Regex: "is the key pressed a digit 0-9?"
        const isDigit = /^\d$/.test(e.key);

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
