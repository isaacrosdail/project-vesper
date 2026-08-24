<script lang="ts" generics="T">
    let {
        items,
        value = $bindable(''),
        toLabel,
        toValue,
        onSelect,
        label,
        placeholder = '',
    }: {
        items: T[];
        value?: string;
        toLabel: (item: T) => string;
        toValue: (item: T) => string;
        placeholder?: string;
        label: string;
        onSelect?: (item: T) => void;
    } = $props();

    $effect(() => {
        if (active < 0) return;
        document.getElementById(`${uid}-opt-${active}`)?.scrollIntoView({ block: 'nearest' });
    });

    const uid = $props.id();
    let el: HTMLDivElement;
    let query = $state('');
    let open = $state(false);
    let active = $state(-1);

    const matches = $derived(
        query
            ? items.filter((it) => toLabel(it).toLowerCase().includes(query.toLowerCase()))
            : items,
    );
    function select(item: T) {
        value = toValue(item);
        el.hidePopover();
        onSelect?.(item);
        query = '';
    }

    function onkeydown(e: KeyboardEvent) {
        if (e.key === 'ArrowDown') {
            el.showPopover();
            active = Math.min(active + 1, matches.length - 1);
        } else if (e.key === 'ArrowUp') {
            active = Math.max(active - 1, 0);
        } else if (e.key === 'Enter') {
            if (open && active >= 0 && active < matches.length) select(matches[active]);
        } else return;
        e.preventDefault();
    }
</script>

<div>
    <input
        type="search"
        role="combobox"
        aria-controls={uid}
        aria-expanded={open}
        aria-label={label}
        aria-autocomplete="list"
        aria-activedescendant={open && active >= 0 ? `${uid}-opt-${active}` : undefined}
        {placeholder}
        {onkeydown}
        bind:value={query}
        style:anchor-name={`--ss-${uid}`}
        onclick={() => el.showPopover()}
        oninput={() => {
            active = -1;
            el.showPopover();
            value = '';
        }} />
    <div
        popover
        ontoggle={(e) => {
            open = e.newState === 'open';
            if (!open) active = -1;
        }}
        id={uid}
        class="results-container"
        role="listbox"
        tabindex="-1"
        bind:this={el}
        style:position-anchor={`--ss-${uid}`}>
        {#each matches as m, i (toValue(m))}
            <button
                type="button"
                role="option"
                tabindex="-1"
                id={`${uid}-opt-${i}`}
                aria-selected={i === active}
                class:active={i === active}
                onclick={() => select(m)}>{toLabel(m)}</button>
        {:else}
            <p>No matches</p>
        {/each}
    </div>
</div>

<style>
    .results-container {
        position: fixed; /* required for anchor positioning */
        top: anchor(bottom);
        left: anchor(left);
        width: anchor-size(width);
        position-try-fallbacks: flip-block;

        margin: 0;
        padding: 0;
        border: none;
        max-height: min(300px, 40vh);
        overflow-y: auto;
        scrollbar-width: thin;
        background: var(--surface-2);
        box-shadow: var(--shadow-md);
        border-radius: 0 0 var(--border-radius) var(--border-radius);

        & > * {
            display: grid;
            grid-template-columns: 1fr auto;
            align-items: center;
            padding: var(--space-sm) var(--space-md);
            background: var(--surface-2);
            &:hover {
                background: var(--surface-3);
            }
        }
        & > .active {
            background: var(--surface-3);
        }
        &:popover-open {
            display: flex;
            flex-direction: column;
        }
        & > * + * {
            border-top: 1px solid var(--line);
        }
    }
</style>
