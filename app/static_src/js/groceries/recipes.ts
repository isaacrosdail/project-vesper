import { initRecipeForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { confirmationManager, openModalForEdit } from '../shared/ui/modal-manager';
import { makeToast } from '../shared/ui/toast';
import { FormDialog, Recipe } from '../types';


/**
 * Adds product to shopping list or increments quantity if already present.
 */
export async function handleAddToShoppingList(
    productId: string,
) {
    const response = await api.shopping_list.addItem(productId);
    const { id, product_id, product_name, unit_type, net_weight } = response.data;

    const existingLi = document.querySelector<HTMLLIElement>(`li[data-product-id="${productId}"]`);
    if (existingLi) {
        const input = existingLi.querySelector('input');
        // const qty = input.value;
        const newQty = String(Number(input.value) + 1);
        input.value = newQty
        makeToast(`Updated ${product_name} quantity to ${newQty}`, 'success');
        return;
    }

    const detailStr = `(${Math.round(net_weight)}${unit_type})`;
    addShoppingListItemToDOM(id, product_id, product_name, detailStr);
    makeToast(`Added ${product_name} to shopping list`, 'success');

}

function initRecipeDetailsModal(modal: FormDialog) {
    console.log(modal)
    const els = {
        modal: modal,
        header: modal.querySelector('.recipe-header'),
        metadata: modal.querySelector('.recipe-metadata'),
        ingredientsList: modal.querySelector('ul')
    };
    console.log(els)
    return els;
}

function deriveRecipeView(recipe: Recipe) {
    const cookTime = 30;
    return {
        title: recipe.name,
        metadata: `Makes: ${recipe.yields} ${recipe.yields_units.toLowerCase()} | ~${cookTime} min`,
        ingredients: recipe.ingredients.map(ing =>
            `${ing.amount_value}${ing.amount_units.toLowerCase()} - ${ing.product_name}`
        )
    };
}

function renderRecipeModal(view, ui) {
    ui.header.textContent = view.title;
    ui.metadata.textContent = view.metadata;
    ui.ingredientsList.replaceChildren(
        ...view.ingredients.map(text => {
            const li = document.createElement('li');
            li.textContent = text;
            return li;
        })
    );
}

function populateRecipeForm(modal: FormDialog, data) {
    const container = modal.querySelector('#ingredients-container');
    const addBtn = modal.querySelector('#add-ingredient');

    data.ingredients.forEach((ing, i) => {
        // get or create the i-th row
        // set product select to ing.product_id
        // set amount to ing.amount_value
        // set units to ing.amount_units
        // TODO: Hacky
        if (i > 0) addBtn.click();
        const row = container.querySelector(`[data-index="${i}"]`);
        if (!row) return;

        row.querySelector(`[name="ingredients[${i}][product_id]"]`).value = String(ing.product_id);
        row.querySelector(`[name="ingredients[${i}][amount_value]"]`).value = String(ing.amount_value);
        row.querySelector(`[name="ingredients[${i}][amount_units]"]`).value = ing.amount_units;

        // if (productSelect) productSelect.value 
        // if (amountInput) amountInput.value 
        // if (unitsSelect) unitsSelect.value 
    });
}

async function openRecipeModal(recipeId: string, recipeModalEls) {
    // const cookTime = 30; // TODO: Un-hardcode this, add to model

    const { data: recipe } = await api.recipes.getById(recipeId);
    renderRecipeModal(deriveRecipeView(recipe), recipeModalEls);
    // const { name: recipe_name, yields, yields_units, ingredients } = recipe.data;

    // // open the modal and sub in THIS recipe's info
    // const modal = document.querySelector<HTMLDialogElement>('#recipe-detail-modal');
    // const modalHeader = modal.querySelector('.recipe-header');
    // const modalMetadata = modal.querySelector('.recipe-metadata');
    // modalHeader.textContent = recipe_name;
    // modalMetadata.textContent = `Makes: ${yields} ${yields_units.toLowerCase()} | ~${cookTime} min`;

    // // for each ingredient, append an li to the ul, and make its textContent = ingredient.name?
    // const ulEl = modal.querySelector('ul')!;
    // ulEl.innerHTML = ''; // nuke current list

    // ingredients.forEach(ing => {
    //     const liEl = document.createElement('li');
    //     liEl.textContent = `${ing.amount_value}${ing.amount_units.toLowerCase()} - ${ing.product_name}`;
    //     ulEl.appendChild(liEl);
    // });

    recipeModalEls.modal.showModal();
}

export async function init() {
    
    const dialog = document.querySelector<FormDialog>('#recipes-entry-dashboard-modal')
    if (!dialog) {
        console.warn('recipes dashboard: #recipes-entry-dashboard-modal not found')
        return
    }
    initRecipeForm(dialog)

    const detailsDialog = document.querySelector('#recipe-detail-modal');
    const recipeModalEls = initRecipeDetailsModal(detailsDialog);
    console.log(recipeModalEls)

    const shoppingList = document.querySelector('.shopping-list');

    // Fires on blur/enter
    shoppingList.addEventListener('change', async (e) => {
        const inputVal = e.target.value;
        // walk up to nearest li, get data-item-id
        const li = e.target.closest('li');
        const { itemId } = li.dataset;
        // patch with new qty, log to confirm
        const response = await api.shopping_list.updateItem(itemId, { quantity_wanted: inputVal });
        makeToast(response.message, 'success');
    })

    shoppingList.addEventListener('click', async (e) => {
        if (e.target.matches('.inline-delete')) {
            const li = e.target.closest('li'); // for data-item-id
            const { itemId } = li.dataset;

            const confirmed = await confirmationManager.show(
                "Are you sure you want to delete this item?"
            );
            if (!confirmed) return;

            await api.shopping_list.deleteItem(itemId);
            li.remove();

            return;
        }
    })


    // DRAFTING: recipe page thing
    const recipeGrid = document.querySelector('#recipes-grid')!;
    recipeGrid.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        if (target.closest('.js-recipe-options')) {
            const button = target.closest('.js-recipe-options');
            const card = target.closest('.recipe-card');
            const { recipeId } = card.dataset;

            const rect = button.getBoundingClientRect(); // dims for pos
            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => {
                            const modal = document.querySelector('#recipes-entry-dashboard-modal')!;
                            openModalForEdit(recipeId, modal, 'Recipe', (data) => {
                                populateRecipeForm(modal, data);
                            });
                        }
                    },
                    {
                        label: 'Delete',
                        action: async () => {
                            const confirmed = await confirmationManager.show(
                                'Are you sure you\'d like to delete this recipe?'
                            );
                            if (!confirmed) return;

                            await api.recipes.delete(recipeId)
                            card.remove()
                        }
                    }
                ]
            });
            return;
        }

        const card = target.closest<HTMLDivElement>('.recipe-card');
        if (card) {
            const recipeId = card.dataset.recipeId;
            console.log(recipeModalEls)
            openRecipeModal(recipeId, recipeModalEls);
        }
    });

    // close modal via X button
    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        if (target.closest('#recipe-detail-modal-close-btn')) {
            const modal = target.closest<HTMLDialogElement>('#recipe-detail-modal');
            modal!.close();
        }
    });
}