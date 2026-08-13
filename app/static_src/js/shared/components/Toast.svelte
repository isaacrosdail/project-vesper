<script module lang="ts">
    export type Toast = {
        id: string;
        title: string;
        message: string;
        type: ToastType;
        durationMS: number;
    };
    export type ToastType = 'info' | 'success' | 'error' | 'warning';
</script>

<script lang="ts">
    let {
        toast,
        onDismiss,
    }: {
        toast: Toast;
        onDismiss: () => void;
    } = $props();
</script>

<div class={['toast', toast.type]} style:--toast-duration="{toast.durationMS}ms">
    {#if toast.title}
        <span>{toast.title}</span>
    {/if}
    <span>{toast.message}</span>
    <button class="toast-dismiss" onclick={() => onDismiss()}>
        <span class="sr-only">Close toast</span>
        <svg class="icon"><use href="#icon-x"></use></svg>
    </button>
</div>

<style>
    /* TODO: remove comment here - lets us interpolate this value? */
    @property --countdown {
        syntax: '<angle>';
        inherits: false;
        initial-value: 360deg;
    }
    @keyframes countdown {
        from {
            --countdown: 360deg;
        }
        to {
            --countdown: 0deg;
        }
    }
    @keyframes toast-countdown {
        from {
            scale: 1 1;
        }
        to {
            scale: 0 1;
        }
    }
    .toast {
        --toast-color: var(--text-muted);
        background-color: color-mix(in srgb, var(--toast-color) 30%, var(--bg));
        border-color: color-mix(in srgb, var(--toast-color) 30%, var(--bg));
        padding: var(--space-xs) var(--space-sm);
        border: solid 1px transparent;
        border-radius: var(--border-radius-mild);
        animation: slide-in 0.2s ease forwards;
        position: relative;
        box-shadow: var(--shadow-md);

        display: flex;
        align-items: center;
        justify-content: space-between;
        overflow: hidden;
    }

    .toast-dismiss {
        position: relative;
        border-radius: 50%;
        animation: countdown var(--toast-duration) linear forwards;
        color: var(--text-muted);
        stroke: var(--text-muted);
        cursor: pointer;

        &:hover {
            color: var(--clr-error);
            stroke: var(--clr-error);
        }

        & svg {
            position: relative;
            z-index: 1;
        }
    }
    .toast::after {
        content: '';
        position: absolute;
        inset: auto 0 0 0;
        height: 3px;
        background-color: var(--toast-color);
        transform-origin: left;
        animation: toast-countdown var(--toast-duration) linear forwards;
    }

    /* Dismissal is a setTimeout in Toaster.svelte, not this animation.
        The global reduced-motion rule limits it to 0.01ms,
        making the bar drain immediately while the toast
        stays active for its full duration, so we'll just drop the indicator entirely.
    */
    @media (prefers-reduced-motion: reduce) {
        .toast::after {
            display: none;
        }
    }

    .toast-exit {
        animation: slide-out 0.2s ease forwards;
    }
    .info {
        --toast-color: blue;
    }
    .success {
        --toast-color: var(--clr-success);
    }
    .warning {
        --toast-color: var(--clr-warning);
    }
    .error {
        --toast-color: var(--clr-error);
    }
</style>
