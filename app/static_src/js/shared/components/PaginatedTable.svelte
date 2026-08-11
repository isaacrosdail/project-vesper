<script lang="ts" generics="T">
    import type { Snippet } from 'svelte';
    import { paginationSlots } from '../pagination';
    let {
        items,
        pageSize = 10,
        getKey,
        header,
        row,
    }: {
        items: T[];
        pageSize?: number;
        getKey: (item: T) => string | number;
        header: Snippet;
        row: Snippet<[T]>;
    } = $props();

    let page = $state(0);
    const maxSlots = $state(5);
    const pageCount = $derived(Math.max(1, Math.ceil(items.length / pageSize)));
    const safePage = $derived(Math.min(page, pageCount - 1));
    const pageRows = $derived(items.slice(safePage * pageSize, (safePage + 1) * pageSize));

    const start = $derived(page * pageSize);
    const from = $derived(items.length === 0 ? 0 : start + 1);
    const to = $derived(Math.min(start + pageSize, items.length)); // TODO(svelte): math is bugged
    const slots = $derived(paginationSlots(safePage, pageCount, maxSlots));
</script>

<table class="table-standard">
    <thead class="table-header">{@render header()}</thead>
    <tbody class="table-body">
        {#each pageRows as item (getKey(item))}
            {@render row(item)}
        {/each}
    </tbody>
</table>

<div class="pagination-section">
    <div class="pagination-controls">
        <button
            class="btn btn-secondary"
            disabled={safePage === 0}
            onclick={() => (page = safePage - 1)}>
            Back
        </button>
        <div class="page-buttons">
            {#each slots as slot (`${slot.kind}-${slot.num}`)}
                <button
                    onclick={() => (page = slot.num)}
                    class="btn btn-ghost"
                    class:active={slot.num === safePage}
                    >{slot.kind === 'page' ? slot.num + 1 : '…'}</button>
            {/each}
        </div>
        <button
            class="btn btn-secondary"
            disabled={safePage === pageCount - 1}
            onclick={() => (page = safePage + 1)}>
            Next
        </button>
    </div>

    <div class="count secondary">{from}-{to} of {items.length}</div>
</div>

<style>
    .pagination-section {
        display: flex;
        flex-direction: column;
        gap: var(--space-xs);

        & .count {
            align-self: center;
        }
    }
    .pagination-controls {
        display: flex;
        justify-content: space-between;

        & .active {
            background: var(--accent-strong);
            color: var(--text-inverse);
        }
    }
    .page-buttons {
        display: flex;
        gap: var(--space-xs);
    }
</style>
