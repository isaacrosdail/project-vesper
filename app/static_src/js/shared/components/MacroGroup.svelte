<script lang="ts">
    import { patchGoals } from '../services/userState.svelte';
    import type { UserMeRead } from '../../apiTypes';
    import SettingRow from './SettingRow.svelte';

    let { goals }: { goals: UserMeRead['goals'] } = $props();

    const CAL_PER_GRAM = { protein: 4, carbs: 4, fat: 9 } as const;

    // null means "no split set yet" - treat as zeroes so the sliders have somewhere to start
    const baseline = () => ({
        protein_pct: goals.protein_pct ?? 0,
        carbs_pct: goals.carbs_pct ?? 0,
        fat_pct: goals.fat_pct ?? 0,
    });

    let draft = $state(baseline());

    const total = $derived(draft.protein_pct + draft.carbs_pct + draft.fat_pct);
    const dirty = $derived(
        draft.protein_pct !== (goals.protein_pct ?? 0) ||
            draft.carbs_pct !== (goals.carbs_pct ?? 0) ||
            draft.fat_pct !== (goals.fat_pct ?? 0),
    );

    const grams = (pct: number, macro: keyof typeof CAL_PER_GRAM) =>
        goals.calories == null
            ? null
            : Math.round((goals.calories * pct) / 100 / CAL_PER_GRAM[macro]);

    async function save() {
        await patchGoals({
            protein_pct: String(draft.protein_pct),
            carbs_pct: String(draft.carbs_pct),
            fat_pct: String(draft.fat_pct),
        });
        draft = baseline(); // patchGoals awaited refreshMe, so goals already holds the new values
    }
</script>

<div class="macro-group">
    <SettingRow
        label="Calories"
        type="number"
        value={goals.calories}
        commit={(v) => patchGoals({ calories: v })} />

    {#each [['protein', 'Protein'], ['carbs', 'Carbs'], ['fat', 'Fat']] as const as [key, label] (key)}
        {@const pct = draft[`${key}_pct`]}
        <div class="macro-row" style:--val={pct}>
            <label class="secondary" for="{key}-pct"
                >{label} {grams(draft[`${key}_pct`], key) ?? '-'}g</label>
            <input
                id="{key}-pct"
                type="range"
                min="0"
                max="100"
                step="5"
                bind:value={draft[`${key}_pct`]} />
            <output for="{key}-pct">{draft[`${key}_pct`]}%</output>
        </div>
    {/each}

    <div class="macro-total" class:off={total !== 100}>
        {total}% of {goals.calories ?? '-'} kcal
    </div>

    {#if dirty}
        <div class="macro-actions">
            <button class="btn btn-primary" disabled={total !== 100} onclick={save}>Save</button>
            <button class="btn btn-secondary" onclick={() => (draft = baseline())}>Revert</button>
        </div>
    {/if}
</div>

<style>
    .macro-row {
        --thumb: 32px;
        --pct: calc(var(--val) / 100);
        display: grid;
        grid-template-columns: 7rem 1fr;
        align-items: center;
        gap: var(--space-sm);
        position: relative;

        output {
            grid-column: 2; /* definite position: this area is the containing block? */
            position: absolute;
            left: calc(var(--pct) * (100% - var(--thumb)) + var(--thumb) / 2);
            top: 50%;
            translate: -50% -50%;
            z-index: 1;
            pointer-events: none;
            opacity: 0;
        }
        input {
            width: 100%;
        }
        input:active + output,
        input:focus-visible + output {
            opacity: 1;
        }
    }
    .macro-total.off {
        color: var(--clr-error);
    }
</style>
