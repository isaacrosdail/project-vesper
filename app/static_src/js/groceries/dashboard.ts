
import { apiRequest } from '../shared/services/api.js';
import { contextMenu } from '../shared/ui/context-menu';
import { confirmationManager, handleDelete, openModalForEdit } from '../shared/ui/modal-manager.js';
import { makeToast } from '../shared/ui/toast.js';
import { initValidation, makeValidator } from '../shared/validators';


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


function updateQty(existingLi: HTMLLIElement) {
    const qtySpan = existingLi.querySelector('.item-qty');
    if (!qtySpan) {
        throw new Error('Quantity span not found');
    }

    const currentQty = parseInt(existingLi.dataset['quantityWanted'] ?? '0', 10);
    const newQty = currentQty + 1;

    qtySpan.textContent = String(newQty);
    existingLi.dataset['quantityWanted'] = String(newQty);
    return newQty;
}

function addShoppingListItemToDOM(itemId: string, productId: string, productName: string, quantity = 1) {
    const ul = document.querySelector('.shopping-list');
    if (!ul) {
        throw new Error('Shopping list <ul> not found')
    }

    document.querySelector('#list-empty')?.remove(); // placeholder text

    // Clone the contents of our template for the new li
    const template = document.querySelector<HTMLTemplateElement>('#shoppinglist-item-template');
    const fragment = template?.content.cloneNode(true) as DocumentFragment;

    const li = fragment.querySelector('li');
    if (!li) throw new Error('li not found in template');

    const itemText = li.querySelector('.item-text');
    const itemQty = li.querySelector('.item-qty');
    if (!itemText || !itemQty) throw new Error('Template structure invalid');

    itemText.textContent = productName;
    itemQty.textContent = String(quantity);
    li.dataset['itemId'] = itemId;
    li.dataset['productId'] = productId;
    li.dataset['quantityWanted'] = String(quantity);
    ul.appendChild(li);
}


/**
 * Adds product to shopping list or increments quantity if already present.
 */
function handleAddToShoppingList(
    productId: string,
) {
    const quantityWanted = 1;
    const url = '/groceries/shopping-lists/items';
    const data = { product_id: productId, quantity_wanted: quantityWanted };

    apiRequest('POST', url, data, {
        onSuccess: (responseData) => {
            const { id, product_id, product_name } = responseData.data;
            const existingLi = document.querySelector<HTMLLIElement>(`li[data-product-id="${productId}"]`);
            if (existingLi) {
                const newQty = updateQty(existingLi);
                makeToast(`Updated ${product_name} quantity to ${newQty}`, 'success');
                return;
            }

            addShoppingListItemToDOM(id, product_id, product_name);
            makeToast(`Added ${product_name} to shopping list`, 'success');
        }
    });
}

export async function init() {
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

            const currentCents = Math.round(Number(priceField.value) * 100);
            const newCentsString = String(currentCents) + e.key;
            const newCents = Number(newCentsString);
            const newPrice = newCents / 100;

            priceField.value = newPrice.toFixed(2);
            priceField.dispatchEvent(new Event('input', { bubbles: true }));

        } else if (e.key === 'Backspace') {
            e.preventDefault();
            const currentCents = Math.round(Number(priceField.value) * 100);

            if (currentCents === 0) {
                priceField.value = '';
            } else {
                const centsAfterBackspace = Math.floor(currentCents / 10);
                const newPrice = centsAfterBackspace / 100;

                priceField.value = newPrice.toFixed(2);
            }

            priceField.dispatchEvent(new Event('input', { bubbles: true }));
        }
    })

    priceField.addEventListener('paste', (e) => {
        e.preventDefault();
        const currentCents = Math.round(Number(priceField.value) * 100);
        const pastedDigits = e.clipboardData?.getData('text') ?? "";
        const nextCentsString = String(currentCents) + pastedDigits;
        const newCents = Number(nextCentsString);
        const newPrice = newCents / 100;

        priceField.value = newPrice.toFixed(2);
        priceField.dispatchEvent(new Event('input', { bubbles: true }));
    })

    const validatePrice = makeValidator('price_at_scan', {
        isFloat: true,
        min: 0.01,
        max: 1000000,
    });

    const validateQuantity = makeValidator('quantity', {
        isInt: true,
        min: 1,
        max: 999
    });

    const validateCalories = makeValidator('calories_per_100g', {
        isFloat: true,
        min: 0,
        max: 900,
    });

    const validateNetWeight = makeValidator('net_weight', {
        isFloat: true,
        min: 0,
    });

    const validateBarcode = makeValidator('barcode', {
        minLength: 8,
        maxLength: 14,
        pattern: /^\d+$/
    });

    const validateProductName = makeValidator('name', {
        maxLength: 80,
    });

    // Validators
    const transactionForm = document.querySelector<HTMLFormElement>('#transactions-form')!;
    initValidation(
        transactionForm,
        {
            price_at_scan: validatePrice,
            quantity: validateQuantity,
            name: validateProductName,
            barcode: validateBarcode,
            calories_per_100g: validateCalories,
            net_weight: validateNetWeight,
        }
    )

    const productForm = document.querySelector<HTMLFormElement>('#products-form')!;
    initValidation(
        productForm,
        {
            name: validateProductName,
            barcode: validateBarcode,
            calories_per_100g: validateCalories,
            net_weight: validateNetWeight,
        }
    )

    // Handle table ellipsis clicks
    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;

        if (target.matches('.js-table-options')) {
            const button = target.closest<HTMLButtonElement>('.row-actions')!;
            const row = target.closest<HTMLElement>('.table-row')!;
            const { itemId, module, subtype } = row.dataset;

            if (!itemId || !module || !subtype) {
                console.error('Missing required data on row');
                return;
            }

            const rect = button.getBoundingClientRect();

            if (subtype === 'products') {
                const modal = document.querySelector(`#${subtype}-entry-dashboard-modal`);
                const url = `/groceries/products/${itemId}`;

                contextMenu.create({
                    position: { x: rect.left, y: rect.bottom },
                    items: [
                        {
                            label: 'Edit',
                            action: () => openModalForEdit(itemId, url, modal, 'Product')
                        },
                        {
                            label: 'Delete',
                            action: () => handleDelete(itemId, url)
                        },
                        {
                            label: 'Add to Shopping List',
                            action: () => handleAddToShoppingList(itemId)
                        }
                    ]
                });
            } else if (subtype === 'transactions') {
                const modal = document.querySelector(`#${subtype}-entry-dashboard-modal`);
                const productId = row.dataset.productId;
                const url = `/groceries/transactions/${itemId}`;

                contextMenu.create({
                    position: { x: rect.left, y: rect.bottom },
                    items: [
                        {
                            label: 'Edit',
                            action: () => openModalForEdit(itemId, url, modal, 'Transaction')
                        },
                        {
                            label: 'Delete',
                            action: () => handleDelete(itemId, url)
                        },
                        {
                            label: 'Add to Shopping List',
                            action: () => handleAddToShoppingList(productId)
                        }
                    ]
                });
            }
        }
    });
}
