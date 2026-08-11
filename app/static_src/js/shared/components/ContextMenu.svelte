
<script module lang="ts">
    type MenuItem = { label: string; action: () => void };

    let menu = $state<{ x: number; y: number; items: MenuItem[] } | null>(null);

    export function openContextMenu(x: number, y: number, items: MenuItem[]) {
        menu = { x, y, items };
    }
    function close() { menu = null; }
</script>

<script lang="ts">
    let menuEl: HTMLDivElement;
</script>

<svelte:window
    onpointerdown={(e) => { if (menu && !menuEl.contains(e.target as Node)) close(); }}
    onkeydown={(e) => e.key === 'Escape' && close()}
    onscroll={close}
/>

{#if menu}
    <div class="context-menu" bind:this={menuEl} style:left={`${menu.x}px`} style:top={`${menu.y}px`}>
        {#each menu.items as i (i.label)}
            <button onclick={() => { i.action(); close(); }}>{i.label}</button>
        {/each}
    </div>
{/if}

<style>
    .context-menu {
        position: fixed;
        display: flex;
        flex-direction: column;
        z-index: 200;
        max-width: 50%;
        background-color: var(--bg);
        border: var(--border-default);
        border-radius: var(--border-radius);

        & > button {
            padding: var(--space-sm) var(--space-md);
        }
        & > button:hover {
            cursor: pointer;
            background-color: var(--accent-subtle);
        }
        & > button:first-child:hover {
            border-radius: var(--border-radius) var(--border-radius) 0 0;
        }
        & > button:last-child:hover {
            border-radius: 0 0 var(--border-radius) var(--border-radius);
        }
        & > button:only-child:hover {
            border-radius: var(--border-radius);
        }
    }
</style>