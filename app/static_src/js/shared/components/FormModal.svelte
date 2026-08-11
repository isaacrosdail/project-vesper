<script lang="ts">
    import type { Snippet } from 'svelte';

    let {
        title,
        open = $bindable(false),
        children,
    }: {
        title: string;
        open?: boolean;
        children: Snippet;
    } = $props();

    let dialogEl: HTMLDialogElement;

    $effect(() => {
        if (open) dialogEl.showModal();
        else dialogEl.close();
    });
</script>

<dialog bind:this={dialogEl} class="form-modal" onclose={() => (open = false)}>
    <div class="modal-header">
        <h2>{title}</h2>
        <button
            type="button"
            class="btn-icon btn-round modal-close"
            aria-label="Close"
            onclick={() => (open = false)}>
            <svg class="icon"><use href="#icon-x"></use></svg>
        </button>
    </div>
    <div class="modal-body">
        {@render children()}
    </div>
</dialog>
