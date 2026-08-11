
<script module lang="ts">
    import ToastItem, { type Toast, type ToastType } from './Toast.svelte';

    let toasts = $state<Toast[]>([]);
    const toastToTimeoutMap = new Map<string, number>();

    export function addToast(
        title: string,
        message: string,
        type: ToastType,
        durationMS = 4000
    ){
        const id = crypto.randomUUID();
        toasts.push({
            id,
            title,
            message,
            type,
            durationMS
        });

        toastToTimeoutMap.set(
            id,
            setTimeout(() => {
                removeToast(id);
            }, durationMS)
        );
    }

    export function removeToast(id: string) {
        const timeout = toastToTimeoutMap.get(id);
        if (timeout) {
            clearTimeout(timeout);
            toastToTimeoutMap.delete(id);
        }
        toasts = toasts.filter((toast) => toast.id !== id);
    }
</script>

<div id="toast-container">
    {#each toasts as toast (toast.id)}
        <ToastItem {toast} onDismiss={() => removeToast(toast.id)} />
    {/each}
</div>

<style>
    #toast-container {
        position: fixed;
        top: calc(1.3 * var(--min-navbar-height));
        right: 1rem;
        z-index: 400;
        display: flex;
        flex-direction: column-reverse;
        gap: var(--space-sm);
        border-radius: var(--border-radius-mild);
    }
</style>