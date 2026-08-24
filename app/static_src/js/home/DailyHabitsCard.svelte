
<script lang="ts">
    import ProgressBar from '../shared/components/ProgressBar.svelte';
    import { habitsState, refreshHabits, toggleEntry } from '../habits/habitsState.svelte';
    import { todayUser } from '../shared/datetime';

    let { openHabitsForm }: {
        openHabitsForm: () => void;
    } = $props();

    refreshHabits();
    
</script>

<section id="daily-habits-card" class="card-dashboard surface grid-2col">
    <div class="card-title">
        <h2>Daily Habits</h2>
        <button class="btn-icon btn-round btn-primary"
            aria-label="TODO"
            onclick={() => openHabitsForm()}>
            <svg class="icon"><use href="#icon-plus"></use></svg>
        </button>
    </div>
    <div>
        <ul class="item-list">
        {#each habitsState.habits as h (h.id)}
            <li class="item" class:completed={h.completed_today}> <!-- TODO: need to implement this -->
                <div class="item-row">
                    <input  type="checkbox" class="habit-checkbox"
                        checked={h.completed_today}
                        onchange={() => toggleEntry(h, todayUser().toString()) }>
                    <span class="item-title">{h.name}</span>
                    <span class="habit-streak">
                        <svg class="streak-icon"><use href="#icon-flame"></use></svg>
                        <span class="streak-count">{h.streak_count || ''}</span>
                    </span>
                </div>
            </li>
        {/each}
        </ul>
    </div>

    {#if habitsState.progress}
    <ProgressBar label="This week" completed={habitsState.progress.completed} total={habitsState.progress.total} />
    {/if}
</section>

<style>
    @keyframes flicker {
        0%, 100% { transform: scaleY(1) scaleX(1); }
        25% { transform: scaleY(1.05) scaleX(0.95); }
        50% { transform: scaleY(0.95) scaleX(1.05); }
        75% { transform: scaleY(1.03) scaleX(0.97); }
    }
    /* Completion flare */
    @keyframes flare {
        0% { transform: scale(1); filter: brightness(1); }
        30% { transform: scale(1.6); filter: brightness(1.5); }
        100% { transform: scale(1); filter: brightness(1); }
    }
    .streak-icon.flare {
        animation: flare 0.4s ease-out forwards, flicker 2s ease-in-out infinite 0.4s;
    }
    /* TODO: Fix up, for fire thing :/ */
    .habit-streak {
    display: inline-flex;
    align-items: center;

    &.completed .streak-icon { display: none; }
    &:has(.streak-count:empty) .streak-icon { display: none; }

    & .streak-icon {
        transition: transform 0.1s ease;
        fill: orange;
        color: orange;
        width: 1em;
        height: 1em;
        transform-origin: bottom center;
        animation: flicker 1.5s ease-in-out infinite;

        &.pop {
        transform: scale(1.4);
        }
    }
    }
</style>