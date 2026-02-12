import { apiRequest } from '../shared/services/api';
import { confirmationManager } from '../shared/ui/modal-manager';
import { contextMenu } from '../shared/ui/context-menu';
import { openModalForEdit } from '../shared/ui/modal-manager';

function addIngredientRow(name = '', amount = '', unit = '') {
    const container = document.querySelector('#ingredients-container')
}

function setupRecipeForm() {
    const addIngredientButton = document.querySelector<HTMLDivElement>('#add-ingredient')!;
    const removeIngredientButton = document.querySelector('.js-remove-ingredient');
    const ingredientsContainer = document.querySelector('#ingredients-container')!; // div! so label+select
    const firstIngredientRow = ingredientsContainer.querySelector('.ingredient-row')!;

    // store initial state of first row for modal cleanup
    const cleanIngredientRow = firstIngredientRow.cloneNode(true);

    const recipesModal = document.querySelector('#recipes-entry-dashboard-modal')!;

    recipesModal.addEventListener('modal:cleanup', () => {
        // clear ingredientsContainer
        ingredientsContainer.innerHTML = '';
        // add back 1 original row
        ingredientsContainer.appendChild(cleanIngredientRow);
    });

    addIngredientButton.addEventListener('click', (e) => {
        const newIdx = ingredientsContainer.querySelectorAll('.ingredient-row').length;

        const clone = firstIngredientRow.cloneNode(true) as HTMLSelectElement;
        clone.removeAttribute('id');

        // get html as str, replace all [0] with [currIdx]
        const html = clone.outerHTML.replace(/\[0\]/g, `[${newIdx}]`);

        const temp = document.createElement('div');
        temp.innerHTML = html;
        const updatedClone = temp.firstElementChild as HTMLElement;

        // clear vals
        updatedClone.querySelectorAll('input').forEach(input => input.value = '');
        updatedClone.querySelectorAll('select').forEach(select => select.selectedIndex = 0);

        // Update label text
        const ingredientNumberSpan = updatedClone.querySelector('.ingredient-number-span');
        ingredientNumberSpan.textContent = `${newIdx + 1}`;

        updatedClone.dataset.index = newIdx;

        ingredientsContainer.appendChild(updatedClone);
    });

}

const myEvent = new CustomEvent('dodo', {
    detail: {},
    bubbles: true,
    cancelable: true,
    composed: false,
});
// document.querySelector('my-el').dispatchEvent(myEvent);

async function openRecipeModal(recipeId: string) {
    // fetch full details for given recipe using id
    // populate modal with said info

    // TODO: Un-hardcode this, add to model
    const cookTime = 30;

    const recipe = await apiRequest('GET', `/groceries/recipes/${recipeId}/details`);
    console.table(recipe);
    const ingredients = recipe.data.ingredients;
    const {name: recipe_name, yields, yields_units} = recipe.data;

    // open the modal and sub in THIS recipe's info
    const modal = document.querySelector<HTMLDialogElement>('#recipe-detail-modal')!;

    const modalHeader = modal.querySelector('.recipe-header')!;
    modalHeader.textContent = recipe_name;

    const modalMetadata = modal.querySelector('.recipe-metadata')!;
    modalMetadata.textContent = `Makes: ${yields} ${yields_units.toLowerCase()} | ~${cookTime} min`;

    // for each ingredient, append an li to the ul, and make its textContent = ingredient.name?
    const ulEl = modal.querySelector('ul')!;
    ulEl.innerHTML = ''; // nuke current list
    console.log(ulEl)
    ingredients.forEach(ing => {
        const liEl = document.createElement('li');
        liEl.textContent = `${ing.amount_value}${ing.amount_units.toLowerCase()} - ${ing.product_name}`;
        console.log(ing.product_name)
        ulEl.appendChild(liEl);
    });

    modal.showModal();
}

// NOTE: We still need to add the "remove" for if we add an ingredient div for entry but change our mind
// Also, we'll need to sort out the form reset cleanup for this
// We could loop to remove all divs that don't have the id of original-dropdown
export async function init() {

    setupRecipeForm();

    // DRAFTING: recipe page thing
    const recipeGrid = document.querySelector('#recipes-grid')!;

    recipeGrid.addEventListener('click', async (e) => {
        if (e.target.closest('.js-recipe-options')) {
            const button = e.target.closest('.js-recipe-options');
            const card = e.target.closest('.recipe-card');
            const recipeId = card.dataset.recipeId;

            // get button dims for {x, y} pos
            const rect = button.getBoundingClientRect();

            console.log("creating menu...")
            contextMenu.create({
                position: { x: rect.left, y: rect.bottom },
                items: [
                    {
                        label: 'Edit',
                        action: () => {
                            console.log('Edit recipe:', recipeId);
                            const modal = document.querySelector('#recipes-entry-dashboard-modal')!;
                            console.log(modal)

                            openModalForEdit(
                                recipeId,
                                `/groceries/recipes/${recipeId}`,
                                modal,
                                'Recipe'
                            )
                        }
                    },
                    {
                        label: 'Delete',
                        action: async () => {
                            const confirmed = await confirmationManager.show(
                                'Are you sure you\'d like to delete this recipe?'
                            );
                            if (!confirmed) return;

                            apiRequest('DELETE', `/groceries/recipes/${recipeId}`, null, {
                                onSuccess: (responseData) => {
                                    card.remove();
                                }
                            });
                        }
                    }
                ]
            });
            return;
        }

        const card = e.target.closest('.recipe-card');
        if (card) {
            const recipeId = card.dataset.recipeId;
            openRecipeModal(recipeId);
        }
    });

    // close modal via X button
    document.addEventListener('click', (e) => {
        if (e.target.closest('#recipe-detail-modal-close-btn')) {
            const modal = e.target.closest('#recipe-detail-modal');
            console.log(modal)
            modal.close();
        }

        else if (e.target.matches('.js-remove-ingredient')) {
            const thisIngredientRow = e.target.closest('.ingredient-row');
            thisIngredientRow.remove();

            // Then re-index all remaining rows
            const ingredientsContainer = document.querySelector('#ingredients-container')!;
            const allRows = ingredientsContainer.querySelectorAll('.ingredient-row')!;
            allRows.forEach((row, newIdx) => {
                // row = curr ingredientRow el
                // newIdx = idx of curr item in arr

                // 1. update data-index to new index
                row.dataset.index = newIdx;

                // 2. replace all [oldIndex] with [newIndex] in the names
                // so replace all [N] with [${newIdx}]
                // before getting outerHTML, sync curr values to attributes
                row.querySelectorAll('input').forEach(input => {
                    input.setAttribute('value', input.value);
                });
                row.querySelectorAll('select').forEach(select => {
                    const selectedOption = select.options[select.selectedIndex];
                    // mark selected option in HTML
                    // Array.from(select.options).forEach(opt => opt.removeAttribute)
                    selectedOption?.setAttribute('selected', '');
                });
                const html = row.outerHTML.replace(
                    new RegExp('\\[\\d+\\]', 'g'),
                    `[${newIdx}]`
                );
                const temp = document.createElement('div');
                temp.innerHTML = html;
                const updatedRow = temp.firstElementChild as HTMLElement;

                // replace old row with updated one
                row.replaceWith(updatedRow)

                // update display number
                const numberSpan = updatedRow.querySelector('.ingredient-number-span');
                console.log(numberSpan);
                if (numberSpan) numberSpan.textContent = String(newIdx + 1);
            })
        }
    });
}