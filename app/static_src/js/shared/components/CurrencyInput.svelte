<script lang="ts">
    import { money } from '../../shared/formatters';

    let {
        value = $bindable(),
        invalid,
        maxCents = 1_000_000,
        label,
    }: {
        value: number;
        label: string;
        invalid?: boolean;
        maxCents?: number;
    } = $props();

    function oninput(e) {
        const val: string = e.currentTarget.value;
        const cents = Math.min(maxCents, Number(val.replace(/\D/g, '')));
        value = cents;
        e.currentTarget.value = money.format(cents / 100);
        console.log('after write:', e.currentTarget.value, '| value prop:', value);
    }
</script>

<input
    type="text"
    inputmode="numeric"
    value={money.format(value / 100)}
    oninput={(e) => oninput(e)}
    aria-invalid={invalid}
    aria-label={label}
    autocomplete="off"
    spellcheck="false" />

<style>
    input[aria-invalid='true'] {
        border-color: var(--clr-error);
    }
    input {
        width: 10ch;
        text-align: right;
        font-variant-numeric: tabular-nums;
    }
</style>
