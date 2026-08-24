<script module lang="ts">
    import type { ProductCategoryEnum, UnitEnum } from '../../apiTypes';

    export type ProductDraft = {
        name: string;
        category: ProductCategoryEnum | '';
        barcode: string;
        calories_per_100g: string;
        net_weight: string;
        unit_type: UnitEnum | '';
    };

    export const emptyProductDraft = (): ProductDraft => ({
        name: '', category: '', barcode: '',
        calories_per_100g: '', net_weight: '', unit_type: '',
    });

    export function toProductPayload(d: ProductDraft) {
        return {
            name: d.name.trim(),
            category: d.category,
            barcode: d.barcode.trim() || null,
            calories_per_100g: d.calories_per_100g ? Number(d.calories_per_100g) : null,
            net_weight: Number(d.net_weight),
            unit_type: d.unit_type,
        };
    }
</script>

<script lang="ts">
    import { CATEGORIES, ALL_UNITS, unitsFor } from '../units';
    import { title } from '../../shared/formatters';

    let { product, idPrefix = 'product' }: {
        product: ProductDraft;
        idPrefix?: string;
    } = $props();

    const allowedUnits = $derived(unitsFor(product.category));

    // category change can strand a now-invalid unit selection
    $effect(() => {
        if (product.unit_type && !allowedUnits.includes(product.unit_type)) {
            product.unit_type = '';
        }
    });
</script>

<div>
    <label for="{idPrefix}-name">Name:</label>
    <input id="{idPrefix}-name" type="text" bind:value={product.name} required>
</div>
<div>
    <label for="{idPrefix}-category">Category:</label>
    <select id="{idPrefix}-category" bind:value={product.category} required>
        <option value="">--</option>
        {#each CATEGORIES as c (c)}<option value={c}>{title(c.replace("_", " & "))}</option>{/each}
    </select>
</div>
<div>
    <label for="{idPrefix}-barcode">Barcode:</label>
    <input id="{idPrefix}-barcode" type="text" inputmode="numeric" bind:value={product.barcode}>
</div>
<div>
    <label for="{idPrefix}-cals">Calories (per 100g):</label>
    <input id="{idPrefix}-cals" type="text" inputmode="decimal" bind:value={product.calories_per_100g}>
</div>
<div class="field-pair field-pair--weighted">
    <div>
        <label for="{idPrefix}-weight">Net Weight:</label>
        <input id="{idPrefix}-weight" type="text" inputmode="decimal" bind:value={product.net_weight} required>
    </div>
    <div>
        <label for="{idPrefix}-units">Units:</label>
        <select id="{idPrefix}-units" bind:value={product.unit_type} required>
            <option value="">--</option>
            {#each ALL_UNITS as u (u)}<option value={u}>{u.replace("_", " ")}</option>{/each}
        </select>
    </div>
</div>
