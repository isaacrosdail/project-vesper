<script lang="ts">
    import { refreshBarchartData, refreshHabits, deleteHabit } from './habitsState.svelte';
    import Hbar from './Hbar.svelte';
    import HabitForm from '../habits/HabitForm.svelte';
    import ListView from './ListView.svelte';
    import HabitDetails from './HabitDetails.svelte';
    import { askConfirm } from '../shared/components/ConfirmDialog.svelte';
    import { openContextMenu } from '../shared/components/ContextMenu.svelte';
    import type { MenuItem } from '../shared/components/ContextMenu.svelte';
    import { fmtDate, todayUser } from '../shared/datetime';

    let habitForm: HabitForm;
    let selectedHabitId = $state<number | null>(null);

    const editHabit = (id: number) => habitForm.open({ editId: id });
    const handleDelete = async (id: number) => {
        if (!(await askConfirm('...'))) return;
        await deleteHabit(id);
    };
    const openHabitMenu = (id: number, x: number, y: number, extra: MenuItem[] = []) =>
        openContextMenu(x, y, [
            { label: 'Edit', action: () => editHabit(id) },
            { label: 'Delete', action: () => handleDelete(id) },
            ...extra,
        ]);

    refreshHabits();
    refreshBarchartData(7);

    const monday = todayUser().subtract({ days: todayUser().dayOfWeek - 1 });
    const sunday = monday.add({ days: 6 });
</script>

<HabitForm bind:this={habitForm} onSuccess={() => refreshHabits()} />

{#if selectedHabitId !== null}
    <HabitDetails habitId={selectedHabitId} wipeId={() => (selectedHabitId = null)} />
{:else}
    <div class="page-header">
        <div>
            <h2 class="page-h2">Week of</h2>
            <div class="timeframe-label secondary">{fmtDate(monday)} - {fmtDate(sunday)}</div>
        </div>
        <button
            class="btn-icon btn-round btn-primary"
            aria-label="Add Habit"
            onclick={() => habitForm.open()}>
            <svg class="icon"><use href="#icon-plus"></use></svg>
        </button>
    </div>
    <ListView onselect={(id) => (selectedHabitId = id)} onOpenMenu={openHabitMenu} />
    <details class="breakdown-group">
        <summary>Completions by Habit</summary>
        <div class="breakdown-content">
            <Hbar />
        </div>
    </details>
{/if}

<style>
    .page-header {
        display: flex;
        justify-content: space-between;
    }

    /* currently just on habits dashboard for the "completions by habit" chart */
    details {
        padding: var(--space-md);
        position: relative;

        & summary {
            cursor: pointer;
        }

        &::after {
            position: absolute;
            content: '';
            bottom: 0;
            left: 0;
            width: 0;
            height: 3px;
            background: var(--accent-strong);
            transition: width 0.1s ease;
        }
    }

    .breakdown-group {
        padding: var(--space-sm);

        & summary {
            cursor: pointer;
        }
    }
</style>
