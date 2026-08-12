<script lang="ts">
    import { userState, patchGoals, patchProfile, patchUser } from '../services/userState.svelte';
    import BodyStatsSection from './BodyStatsSection.svelte';
    import SettingRow from './SettingRow.svelte';
    import LocationRow from './LocationRow.svelte';
    import MacroGroup from './MacroGroup.svelte';

    let sidebarEl: HTMLElement;

    const TIMEZONES = Intl.supportedValuesOf('timeZone')
        .filter((tz) => !tz.startsWith('Etc'))
        .map((tz) => [tz, tz] as const);
    const UNIT_SYSTEMS = [
        ['metric', 'Metric'],
        ['imperial', 'Imperial'],
    ] as const;
    const HOUR_CYCLES = [
        ['h12', '12H'],
        ['h23', '24H'],
    ] as const;
</script>

<aside popover id="profile-sidebar" class="profile-sidebar" bind:this={sidebarEl}>
    {#if userState.me}
        {@const me = userState.me}
        <button class="sidebar-close" aria-label="Close" onclick={() => sidebarEl.hidePopover()}
            ><kbd>ESC</kbd></button>

        <section class="sidebar-section">
            <h3>Account</h3>
            <SettingRow
                label="Timezone"
                type="select"
                options={TIMEZONES}
                value={me.timezone}
                commit={(v) => patchUser({ timezone: v })} />
        </section>

        <section class="sidebar-section">
            <h3>Settings</h3>
            <SettingRow
                label="Unit System"
                type="select"
                options={UNIT_SYSTEMS}
                value={me.profile.unit_system}
                commit={(v) => patchProfile({ unit_system: v })} />
            <SettingRow
                label="Time Format"
                type="select"
                options={HOUR_CYCLES}
                value={me.profile.hour_cycle}
                commit={(v) => patchProfile({ hour_cycle: v })} />
            <LocationRow profile={me.profile} />
        </section>

        <section class="sidebar-section">
            <h3>Nutrition Goals</h3>
            <!-- Calories & Macros slider -->
            <MacroGroup goals={me.goals} />
            <SettingRow
                label="Weight"
                type="number"
                value={me.goals.weight}
                commit={(v) => patchGoals({ weight: v })} />
        </section>

        <BodyStatsSection profile={me.profile} />

        <form action="/logout" method="post">
            <input type="hidden" name="csrf_token" value={window.csrfToken} />
            <button class="btn btn-destructive" type="submit">Log out</button>
        </form>

        {#if document.documentElement.dataset.dev === 'true'}
            <div class="sidebar-section devtools-section">
                <h3>Dev Tools</h3>
                <div class="my-grid">
                    <div class="links">
                        <a class="btn btn-primary" href="/pillars">Pillars</a>
                        <a class="btn btn-secondary" href="/devtools/style_reference">Style Ref</a>
                    </div>
                </div>
            </div>
        {/if}
    {/if}
</aside>

<style>
    .sidebar-close {
        align-self: start;
    }

    .profile-sidebar {
        overflow-y: auto;
        position: fixed;
        top: 0;
        right: 0;
        width: 280px;
        z-index: 1000;
        height: 100%;
        background: var(--bg);
        flex-direction: column;
        gap: var(--space-md);
        padding: var(--space-md);
        border-left: 2px solid var(--accent-strong);
        /* transform: translateX(100%); */
        transition:
            transform 0.2s ease,
            display 0.2s allow-discrete,
            overlay 0.2s allow-discrete;

        &:popover-open {
            display: flex;
            transform: translateX(0);
        }

        @starting-style {
            &:popover-open {
                transform: translateX(100%);
            }
        }

        &::backdrop {
            background: rgba(0, 0, 0, 0.4);
        }

        /* &.open { transform: translateX(0); } */

        & .logout {
            justify-self: end;
        }

        /* TODO: move elsewhere? */
        & .devtools-section {
            & .my-grid {
                display: grid;
                grid-template-areas:
                    'links links'
                    'reset reset';
                gap: var(--space-sm);
            }
            & .reset {
                grid-area: reset;
            }
            & .links {
                grid-area: links;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: var(--space-sm);
            }
            & a,
            & button {
                font-size: var(--font-size-sm);
                height: 40px;
            }
        }
    }
</style>
