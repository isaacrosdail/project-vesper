<script lang="ts">
    import { tasksState } from './tasksState.svelte';

    let {
        onOpenDetails,
    }: {
        onOpenDetails: (id: number) => void;
    } = $props();

    $effect(() => {
        if (activeIndex < 0) return;
        const id = matches[activeIndex]?.id;
        if (id === undefined) return;
        document.getElementById(`task-opt-${id}`)?.scrollIntoView({ block: 'nearest' });
    });

    let el: HTMLDivElement;
    let query = $state('');
    let activeIndex = $state(-1);
    const matches = $derived(
        query
            ? tasksState.tasks.filter((t) => t.name.toLowerCase().includes(query.toLowerCase()))
            : [],
    );
    const activeMatch = $derived(activeIndex >= 0 ? matches[activeIndex] : undefined);
</script>

<div
    bind:this={el}
    popover
    id="search-popover"
    class="search-popover popover-overlay"
    ontoggle={(e) => {
        if (e.newState === 'closed') {
            query = '';
            activeIndex = -1;
        }
    }}>
    <div class="search-field">
        <input
            type="search" class="search-input"
            placeholder="Search for a task"
            role="combobox"
            aria-controls="search-results"
            aria-expanded={matches.length > 0}
            aria-activedescendant={matches[activeIndex] ? `task-opt-${activeMatch?.id}` : undefined}
            oninput={() => (activeIndex = -1)}
            onkeydown={(e) => {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    activeIndex = Math.min(activeIndex + 1, matches.length - 1);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    activeIndex = Math.max(activeIndex - 1, -1);
                } else if (e.key === 'Enter' && activeMatch?.id) {
                    e.preventDefault();
                    el.hidePopover();
                    onOpenDetails(activeMatch.id);
                }
            }}
            bind:value={query} />
        {#if query.length > 0}
            <button class="clear-input-btn" onclick={() => {
                query = ''; activeIndex = -1;
            }}
                aria-label="Clear search">
                <svg class="icon"><use href="#icon-x"></use></svg>
            </button>
        {/if}
    </div>
    <div class="results-container" role="listbox" id="search-results">
        {#each matches as t, i (t.id)}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <div
                role="option"
                id="task-opt-{t.id}"
                tabindex="-1"
                aria-selected={i === activeIndex}
                class:active={i === activeIndex}
                onclick={() => {
                    el.hidePopover();
                    onOpenDetails(t.id);
                }}>
                {t.name}
            </div>
        {/each}
    </div>
</div>

<style>
    .search-field {
        position: relative;
        display: flex;
    }
    .clear-input-btn {
        position: absolute;
        right: var(--space-xs);
        top: 50%;
        transform: translateY(-50%);
        border-radius: var(--border-radius);

        &:hover {
            background: var(--surface-3);
        }
    }
    .search-input {
        padding-right: 2rem;
    }
    [id^='task-opt-'] {
        /* border-radius: var(--border-radius); */
        padding: 0 var(--space-xs);
    }
    .active,
    [id^='task-opt-']:hover {
        cursor: pointer;
        border-left: 2px solid var(--accent-subtle);
        background: var(--surface-3);
    }
    .results-container {
        margin-top: 1rem;
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
    }
</style>
