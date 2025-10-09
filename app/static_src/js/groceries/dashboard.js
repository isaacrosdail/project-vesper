// Entry point for groceries JS
import { confirmationManager } from '../shared/ui/modal-manager.js';
import { apiRequest } from '../shared/services/api.js';

    const unitGroups = {
        weight: ['g', 'kg', 'oz', 'lb'],
        volume: ['ml', 'l', 'fl_oz']
    }
    // Map categories to groups: keys are categories, values are groups (in turn, keys for above dict)
    const unitOptionsMap = {
        beverages: "volume",
        condiments_sauces: "volume",
        fats_oils: ["weight", "volume"],

        fruits: "weight",
        vegetables: "weight", 
        legumes: "weight",
        grains: "weight",
        bakery: "weight",
        dairy_eggs: ["weight", "volume"],
        meats: "weight",
        seafood: "weight",
        snacks: "weight",
        sweets: "weight",
        processed_convenience: ["weight", "volume"],
        supplements: ["weight", "volume"]
    }

    /**
     * Handles click actions (increment, decrement, delete) on shopping list items.
     * Dispatches to appropriate API call and updates the DOM onSuccess accordingly.
     * @param {*} e - Click event from listener
     * @returns 
     */
    async function handleListActionClick(e) {
        const action = e.target.dataset.action;
        if (!action) return;

        const item = e.target.closest('.shoppinglist-item');
        const itemId = item?.dataset.itemId;
        const currentQuantity = parseInt(item?.dataset.quantityWanted, 10);
        const container = e.target.closest('.qty-controls'); // parent to subsequently grab span for qty to edit text
        const qtySpan = container?.querySelector('.item-qty'); // then grab span for editing qty after fetches
        const url = `/groceries/shopping_list_items/${itemId}`;


        switch(action) {
            case "increment": {
                const newQty = currentQuantity + 1;
                const incrementBtn = e.target;
                incrementBtn.disabled = true;
                apiRequest('PATCH', url, () => {
                    qtySpan.textContent = newQty;
                    item.dataset.quantityWanted = newQty;
                    incrementBtn.disabled = false;
                }, { quantity_wanted: newQty });
                break;
            }

            case "decrement": {
                const newQty = currentQuantity - 1;
                e.target.disabled = true;

                if (newQty === 0) {
                    const confirmed = await confirmationManager.show("Are you sure? This will delete the item from your shopping list.");
                    if (!confirmed) {
                        e.target.disabled = false;
                        return;
                    };
                    apiRequest('DELETE', url, () => item.remove());
                } else {
                    apiRequest('PATCH', url, () => {
                        // update DOM qty display
                        qtySpan.textContent = newQty;
                        item.dataset.quantityWanted = newQty;
                        e.target.disabled = false;
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
     * @param {*} e Change event from a category <select>
     * @returns 
     */
    function handleUnitFiltering(e) {
        const form = e.target.closest('form');
        if (!form) return;

        const categoryElement = form.querySelector('[name="category"]');
        const unitSelect = form.querySelector('[name="unit_type"]');
        if (!categoryElement || !unitSelect) return;

        const categorySelection = categoryElement.value;
        const unitTypes = unitSelect.querySelectorAll('option');

        // 2-step lookup with dict keys to store appropriate list of allowed units for given selection in allowedUnits
        const allowedUnits = unitGroups[unitOptionsMap[categorySelection]];

        unitTypes.forEach(option => {
            option.hidden = !allowedUnits.includes(option.value);
        });
    }

    function toggleProductFields(e) {
        const form = e.target.closest('form');
        const productFields = form.querySelectorAll('.product-field input, .product-field select');
        const isNew = (e.target.value === '__new__');

        productFields.forEach(field => {
            field.parentElement.hidden = !isNew;
            field.disabled = !isNew;
        })
    }


export function init() {
    const transactionModal = document.querySelector('#transactions-entry-dashboard-modal');
    const priceField = transactionModal.querySelector('[name="price_at_scan"]');

    document.addEventListener('click', handleListActionClick);

    document.addEventListener('change', (e) => {
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
            field.parentElement.hidden = true;
            field.disabled = true;
        })
    })
}
