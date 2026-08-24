<script lang="ts">
    import { createHotkey, formatForDisplay, getHotkeyRegistrations } from "@tanstack/svelte-hotkeys";

    const registrations = getHotkeyRegistrations();
    let el: HTMLElement;
    createHotkey('Shift+Space', () => {
        console.log("fired", el);
        el.togglePopover();
    },
    () => ({
        meta: { name: 'Show hotkeys available' }, // give a name / description
    }));

    createHotkey('H', () => {
        const wrapper = document.querySelector('.wrapper');
        wrapper?.classList.toggle('sidebar-open');
    },
    () => ({
        meta: { name: 'Toggle left sidebar (if available)' },
    }));

    // TODO: to open profile sidebar?
    // createHotkey('P', )

    // TODO: move back to Tasks post-commit
</script>

<section bind:this={el} popover class="popover">
    <h2>Active Hotkeys:</h2>

    {#each registrations.hotkeys as hk}
        <p>{hk.options.meta?.name}: <kbd>{formatForDisplay(hk.hotkey)}</kbd></p>
    {/each}
</section>

<style>
    .popover {
        inset: 0;
        top: -50%;
        margin: auto;
        padding: var(--space-md);
        width: fit-content;
        height: fit-content;
        border: 2px solid var(--accent-strong);
    }
</style>