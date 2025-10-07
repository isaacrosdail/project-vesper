// Entry point for groceries JS
import { confirmationManager } from '../shared/ui/modal-manager.js';
import { apiRequest } from '../shared/services/api.js';

export function init() {
    if (!document.querySelector('[data-module="groceries"]')) {
        return;
    }

    document.addEventListener('click', async (e) => {
        const action = e.target.dataset.action;
        if (!action) return;

        const item = e.target.closest('.shoppinglist-item');
        const itemId = item?.dataset.itemId;
        const currentQuantity = parseInt(item?.dataset.quantityWanted, 10);
        const container = e.target.closest('.qty-controls'); // parent to subsequently grab span for qty to edit text
        const qtySpan = container?.querySelector('.item-qty'); // then grab span for editing qty after fetches

        const url = `/groceries/shopping_list_items/${itemId}`;

        switch(action) {
            case "increment":
                const increasedQty = currentQuantity + 1;
                const incrementBtn = e.target;
                incrementBtn.disabled = true;

                apiRequest('PATCH', url, () => {
                    // update DOM qty display
                    qtySpan.textContent = increasedQty;
                    item.dataset.quantityWanted = increasedQty;
                    incrementBtn.disabled = false;
                }, { quantity_wanted: increasedQty });

                break;

            case "decrement":
                const decreasedQty = currentQuantity - 1;
                const decrementBtn = e.target;
                decrementBtn.disabled = true;

                if (decreasedQty === 0) {
                    // Effectively a delete for item
                    const confirmed = await confirmationManager.show("Are you sure? This will delete the item from your shopping list.");
                    if (!confirmed) {
                        decrementBtn.disabled = false;
                        return;
                    };

                    apiRequest('DELETE', url, () => {
                        item.remove();
                    });

                } else {
                    apiRequest('PATCH', url, () => {
                        // update DOM qty display
                        qtySpan.textContent = decreasedQty;
                        item.dataset.quantityWanted = decreasedQty;
                        decrementBtn.disabled = false;
                    }, { quantity_wanted: decreasedQty });
                }
                break;

            case "delete":
                const confirmed = await confirmationManager.show("Are you sure you want to delete this item?");
                if (!confirmed) return;

                apiRequest('DELETE', url, () => {
                    item.remove();
                });
                break;
        }
    });
}