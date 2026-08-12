<script lang="ts">
    import { patchProfile } from '../services/userState.svelte';
    import type { UserMeRead } from '../../apiTypes';

    let { profile }: { profile: UserMeRead['profile'] } = $props();

    // country is ISO 3166-1 alpha-2; schemas.py:91 validates it through pycountry
    // and models.py:152 is String(2). Intl.DisplayNames turns the codes into labels,
    // so the only thing to maintain is the code list.
    const CODES = ['US', 'GB', 'AU', 'CA', 'DE', 'IT', 'RU', 'NO'] as const;
    const regions = new Intl.DisplayNames(['en'], { type: 'region' });
    const COUNTRIES = CODES.map((c) => [c, regions.of(c) ?? c] as const);

    let cityEl: HTMLInputElement;
    let countryEl: HTMLSelectElement;

    async function commit() {
        const city = cityEl.value.trim();
        const country = countryEl.value;
        // service.py:100 rejects one without the other, so there's nothing to send yet
        if (!city || !country) return;
        if (city === profile.city && country === profile.country) return;
        try {
            await patchProfile({ city, country });
        } catch (err) {
            cityEl.value = profile.city ?? '';
            countryEl.value = profile.country ?? '';
            throw err;
        }
    }
</script>

<div class="setting-row">
    <span class="secondary">Location</span>
    <div class="location-fields">
        <input bind:this={cityEl} value={profile.city ?? ''} placeholder="City" onchange={commit} />
        <select bind:this={countryEl} onchange={commit}>
            <option value="" disabled selected={!profile.country}>Country</option>
            {#each COUNTRIES as [code, name] (code)}
                <option value={code} selected={code === profile.country}>{name}</option>
            {/each}
        </select>
    </div>
</div>

<style>
    .location-fields {
        display: flex;
        flex-direction: column;
        gap: var(--space-xs);
        justify-self: end;
    }
    .location-fields input,
    .location-fields select {
        width: 120px;
    }
</style>
