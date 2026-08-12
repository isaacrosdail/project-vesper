<script lang="ts">
    import { divmod } from '../utils';
    import { patchProfile } from '../services/userState.svelte';
    import type { UserMeRead } from '../../apiTypes';
    import SettingRow from './SettingRow.svelte';

    let { profile }: { profile: UserMeRead['profile'] } = $props();

    const SEXES = [
        ['', '-'],
        ['m', 'M'],
        ['f', 'F'],
    ] as const;
    const cmToFtIn = (cm: number) => divmod(cm / 2.54, 12);

    let ftEl: HTMLInputElement;
    let inEl: HTMLInputElement;
    const ftIn = $derived(profile.height_cm == null ? [null, null] : cmToFtIn(profile.height_cm));

    async function commitHeight() {
        if (!ftEl.value && !inEl.value) return;
        const cm = Math.round((Number(ftEl.value) * 12 + Number(inEl.value)) * 2.54);
        await patchProfile({ height_cm: String(cm) });
    }
</script>

<section class="sidebar-section">
    <h3>Body Stats</h3>
    <SettingRow
        label="Sex"
        type="select"
        value={profile.sex}
        options={SEXES}
        commit={(v) => patchProfile({ sex: v })} />
    <SettingRow
        label="Birth Date"
        type="date"
        value={profile.birth_date}
        commit={(v) => patchProfile({ birth_date: v })} />

    {#if profile.unit_system === 'imperial'}
        <div class="setting-row">
            <span class="secondary">Height</span>
            <div class="height-fields">
                <input
                    type="number"
                    bind:this={ftEl}
                    value={ftIn[0] ?? ''}
                    placeholder="ft"
                    onchange={commitHeight} />
                <input
                    type="number"
                    bind:this={inEl}
                    value={ftIn[1] ? Math.round(ftIn[1]) : ''}
                    placeholder="in"
                    onchange={commitHeight} />
            </div>
        </div>
    {:else}
        <SettingRow
            label="Height (cm)"
            type="number"
            value={profile.height_cm}
            commit={(v) => patchProfile({ height_cm: v })} />
    {/if}
</section>

<style>
    .height-fields {
        display: flex;
        gap: var(--space-xs);
        justify-self: end;
    }
    .height-fields input {
        width: 60px;
    }
</style>
