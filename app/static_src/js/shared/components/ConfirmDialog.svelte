<script module lang="ts">
    let message = $state<string | null>(null);
    let resolver: ((v: boolean) => void) | null = null;

    export function askConfirm(msg: string): Promise<boolean> {
        resolver?.(false);
        const { promise, resolve } = Promise.withResolvers<boolean>();
        message = msg;
        resolver = resolve;
        return promise;
    }

    function settle(value: boolean) {
        resolver?.(value);
        resolver = null;
        message = null;
    }
</script>

<script lang="ts">
    let dialog: HTMLDialogElement;

    $effect(() => {
        if (message !== null) dialog.showModal();
        else dialog.close();
    });
</script>

<dialog id="confirmation-modal" bind:this={dialog} onclose={() => settle(false)}>
    <div class="confirmation-content">
        <p class="confirmation-message">{message}</p>
        <div class="confirmation-actions">
            <button class="btn btn-primary" onclick={() => settle(true)}>OK</button>
            <button class="btn btn-secondary" onclick={() => settle(false)}>Cancel</button>
        </div>
    </div>
</dialog>

<style>
    /* Confirmation modal variant's content */
    #confirmation-modal[open] {
        display: grid;
        grid-template-columns: 1fr;
        place-items: center;
        margin: auto;
        inset: 0;
    }
    .confirmation-content {
        text-align: center;
    }
    .confirmation-message {
        padding: var(--space-sm);
    }
    .confirmation-actions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--space-md);
    }
</style>
