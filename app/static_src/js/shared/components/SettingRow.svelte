<script lang="ts">
    type Option = readonly [value: string, label: string];

    let {
        label,
        value,
        type = 'text',
        options,
        commit,
    }: {
        label: string;
        value: string | number | null;
        type?: 'text' | 'number' | 'date' | 'select';
        options?: readonly Option[];
        commit: (value: string) => Promise<void>;
    } = $props();

    async function onchange(e: Event & { currentTarget: HTMLInputElement | HTMLSelectElement }) {
        const el = e.currentTarget;
        try {
            await commit(el.value);
        } catch (err) {
            // `value` never changed, so Svelte won't re-sync the DOM on its own.
            el.value = value == null ? '' : String(value);
            throw err; // main.ts's unhandledrejection handler toasts it
        }
    }
</script>

<div class="setting-row">
    <span class="secondary">{label}</span>
    {#if type === 'select'}
        <select {onchange}>
            {#each options ?? [] as [val, text] (val)}
                <option value={val} selected={val === value}>{text}</option>
            {/each}
        </select>
    {:else}
        <input {type} value={value ?? ''} {onchange} />
    {/if}
</div>

<style>
    :global(.setting-row) {
        display: grid;
        grid-template-columns: auto 1fr;
        align-items: center;
        gap: var(--space-sm);

        & > :last-child {
            justify-self: end;
            font-size: var(--font-size-sm);
        }
        & :global(input),
        & :global(select) {
            margin: 0;
            padding: var(--space-xs);
            width: 90px;
            height: 30px;
        }
    }
</style>
