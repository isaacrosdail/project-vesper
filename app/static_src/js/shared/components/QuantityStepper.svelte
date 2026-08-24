<script lang="ts">
    import { debounce } from '../../shared/utils';

    let {
        value = $bindable(),
        label,
        min = 1,
        max = 999,
        onCommit,
    }: {
        value: number;
        label: string;
        min?: number;
        max?: number;
        onCommit?: (n: number) => void;
    } = $props();

    let local = $state(value);
    const commit = debounce(() => onCommit?.(local), 400);
    const uid = $props.id();

    function set(n: number) {
        local = Math.min(max, Math.max(min, n));
        value = local;
        commit();
    }

    function handleInput(e: Event & { currentTarget: HTMLInputElement }) {
        const parsed = Number.parseInt(e.currentTarget.value, 10);
        if (Number.isInteger(parsed) && parsed >= min) set(parsed);
        else e.currentTarget.value = String(local);
    }
</script>

<div class="stepper">
    <button
        type="button"
        class="btn btn-secondary"
        onclick={() => set(local - 1)}
        disabled={local <= min}
        aria-label="Decrease quantity of {label}"
        aria-controls={uid}>
            <svg class="icon" aria-hidden="true"><use href="#icon-minus"></use></svg>
    </button>

    <input
        id={uid}
        type="text"
        inputmode="numeric"
        autocomplete="off"
        spellcheck="false"
        aria-live="polite"
        bind:value={local}
        oninput={handleInput}
        onkeydown={(e) => {
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                set(local+1);
            }
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                set(local-1);
            }
        }}
        aria-label="Quantity of {label}" />

    <button
        type="button"
        class="btn btn-secondary"
        onclick={() => set(local + 1)}
        disabled={local >= max}
        aria-label="Increase quantity of {label}"
        aria-controls={uid}>
            <svg class="icon" aria-hidden="true"><use href="#icon-plus"></use></svg>
    </button>
</div>

<style>
    .stepper {
        display: inline-flex;
        flex: none;
        align-items: center;
        border: var(--border-default);
        border-radius: var(--border-radius);
        overflow: hidden;

        & input {
            width: 4ch;
            padding: 0;
            text-align: center;
            font-variant-numeric: tabular-nums;
            border: 0;
            border-radius: 0;
            background: transparent;
        }
        & button {
            display: flex;
            align-items: center;
            justify-content: center;
            aspect-ratio: 1;
            padding: 0;
            color: var(--text-muted);

            &:hover:not(:disabled) {
                color: var(--text);
                background: var(--surface-3);
            }
        }
    }
</style>
