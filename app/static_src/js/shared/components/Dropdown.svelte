<script lang="ts" generics="T extends string">
    let {
        opts,
        label,
        onSelect,
    }: {
        opts: readonly [label: string, value: T][];
        label: string;
        onSelect: (value: T) => void;
    } = $props();

    const uid = $props.id();
    let isOpen = $state(false);
</script>

<button class="dropdown-toggle surface" popovertarget={uid} style:anchor-name={`--dd-${uid}`}>
    <span class="dropdown-toggle-label">{label}</span>
    <span class="dropdown-toggle-chevron">
        <svg class="icon" class:flip={isOpen}><use href="#icon-chevron"></use></svg>
    </span>
</button>
<div
    popover
    id={uid}
    class="dropdown-menu surface"
    style:position-anchor={`--dd-${uid}`}
    ontoggle={(e) => (isOpen = e.newState === 'open')}>
    {#each opts as opt (opt[0])}
        <button popovertarget={uid} popovertargetaction="hide" onclick={() => onSelect(opt[1])}
            >{opt[0]}</button>
    {/each}
</div>

<style>
    .dropdown-toggle {
        display: inline-flex;
        gap: var(--space-sm);
        align-items: center;
        padding: var(--space-xs) var(--space-sm);
        white-space: nowrap;
        background-color: var(--surface-2);
        border: var(--border-default);
        border-radius: var(--border-radius);
    }

    .dropdown-toggle-chevron,
    .dropdown-toggle-label {
        pointer-events: none;
    }
    .dropdown-toggle-chevron svg {
        transition: transform 0.2s ease;

        &.flip {
            transform: rotate(180deg);
        }
    }

    .dropdown-menu {
        width: anchor-size(width);
        top: anchor(bottom);
        left: anchor(left);
        position: fixed; /* required for anchor positioning */
        margin: 0;
        padding: 0;
        box-shadow: var(--shadow-md);

        & > button {
            display: block;
            width: 100%;
            padding: var(--space-sm) var(--space-md);
            text-align: left;
        }
        & > button:hover {
            background-color: var(--accent-subtle);
        }
    }
    .dropdown-menu .active {
        background: var(--accent-subtle);
    }
</style>
