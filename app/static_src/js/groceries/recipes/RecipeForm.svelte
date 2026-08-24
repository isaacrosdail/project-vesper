<script lang="ts">
    import { api } from '../../shared/services/api';
    import { addToast } from '../../shared/components/Toaster.svelte';
    import { recipeForm, refreshSlots } from '../groceriesState.svelte';
    import type { ProductRead, UnitEnum } from '../../apiTypes';
    import FormModal from '../../shared/components/FormModal.svelte';

    const UNITS: UnitEnum[] = ['g', 'kg', 'oz', 'lb', 'ml', 'l', 'fl_oz', 'ea'];

    type IngredientDraft = { product_id: string; amount_value: string; amount_units: string };
    const emptyIngredient = (): IngredientDraft =>
        ({ product_id: '', amount_value: '', amount_units: '' });

    let products = $state<ProductRead[]>([]);
    function blankForm() {
        return {
            name: '',
            yields: '',
            yields_units: '',
            ingredients: [emptyIngredient()],
        }
    }
    let form = $state(blankForm());

    const title = $derived(recipeForm.editingId !== null ? 'Edit Recipe' : 'Add Recipe');

    // TODO(forms): Rope in our frontend validation here?
    const isValid = $derived(
        form.name.trim().length > 0
        && Number(form.yields) > 0
        && form.yields_units !== ''
        && form.ingredients.every(i => i.product_id && Number(i.amount_value) > 0 && i.amount_units)
    );

    $effect(() => {
        if (!recipeForm.open) return;
        if (!products.length) {
            api.products.getAll().then(({ data }) => products = data);
        }
        if (recipeForm.editingId !== null) {
            api.recipes.getById(String(recipeForm.editingId)).then(({ data }) => {
                form.name = data.name;
                form.yields = String(data.yields);
                form.yields_units = data.yields_units;
                form.ingredients = data.ingredients.map(i => ({
                    product_id: String(i.product_id),
                    amount_value: String(i.amount_value),
                    amount_units: i.amount_units,
                }));
            });
        } else {
            form = blankForm();
        }
    });

    async function submit(e: SubmitEvent) {
        e.preventDefault();
        const payload = {
            name: form.name.trim(),
            yields: Number(form.yields),
            yields_units: form.yields_units,
            ingredients: form.ingredients.map(i => ({
                product_id: Number(i.product_id),
                amount_value: Number(i.amount_value),
                amount_units: i.amount_units,
            })),
        };
        const { message } = recipeForm.editingId !== null
            ? await api.recipes.patch(String(recipeForm.editingId), payload)
            : await api.recipes.post(payload);
        addToast(message, '', 'success');
        recipeForm.open = false;
        await refreshSlots();
    }
</script>

<FormModal {title} bind:open={recipeForm.open}>
    <form class="form-column" onsubmit={submit}>
        <div>
            <label for="recipe-name">Recipe Name:</label>
            <input id="recipe-name" type="text" bind:value={form.name} required>
        </div>
        <div class="field-pair field-pair--weighted">
            <div>
                <label for="recipe-yields">Yields:</label>
                <input id="recipe-yields" type="text" inputmode="decimal" bind:value={form.yields}>
            </div>
            <div>
                <label for="recipe-yields-units">Units:</label>
                <select id="recipe-yields-units" bind:value={form.yields_units} required>
                    <option value="">--</option>
                    {#each UNITS as unit (unit)}<option value={unit}>{unit}</option>{/each}
                </select>
            </div>
        </div>

        <h3 class="ingredients-header">Ingredients:</h3>
        {#each form.ingredients as ing, i (`${ing.product_id}-${i}`)}
            <div class="ingredient-row">
                <select aria-label="Product" bind:value={ing.product_id} required>
                    <option value="">Product</option>
                    {#each products as p (p.id)}<option value={String(p.id)}>{p.name}</option>{/each}
                </select>
                <input aria-label="Amount" type="text" inputmode="decimal" placeholder="35"
                    bind:value={ing.amount_value} required>
                <select aria-label="Units" bind:value={ing.amount_units} required>
                    <option value="">Units</option>
                    {#each UNITS as unit (unit)}<option value={unit}>{unit}</option>{/each}
                </select>
                {#if form.ingredients.length > 1}
                    <button type="button" class="btn-icon btn-square"
                        onclick={() => form.ingredients.splice(i, 1)}>✕</button>
                {/if}
            </div>
        {/each}
        <button type="button" class="btn-soft" onclick={() => {
            form.ingredients.push(emptyIngredient());
            console.log($state.snapshot(form.ingredients).length);
        }}>
            + Add ingredient
        </button>
        <div class="form-actions">
            <button type="submit" class="btn btn-primary" disabled={!isValid}>Save</button>
        </div>
    </form>
</FormModal>

<style>
.ingredient-row {
  position: relative;
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: var(--space-sm);
  border-left: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  /* background: var(--surface-3); */
  padding: var(--space-md);
  align-items: end;

  &:only-of-type .js-remove-ingredient {
    display: none;
  }
}
.btn-remove-ingredient {
  position: absolute;
  /* top: 0; */
  right: -20px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--surface-2);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 0.15s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ingredient-row:hover .btn-remove-ingredient {
  opacity: 1;
}
.btn-remove-ingredient:hover {
  color: var(--clr-error);
  border-color: var(--clr-error);
}
</style>