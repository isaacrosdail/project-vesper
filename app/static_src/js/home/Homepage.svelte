
<script lang="ts">
    import GreetingCard from './GreetingCard.svelte';
    import HabitForm from '../habits/HabitForm.svelte';
    import DailyMetricsForm from '../metrics/DailyMetricsForm.svelte';
    import TaskForm from '../tasks/TaskForm.svelte';
    import TimeEntryForm from '../time_tracking/TimeEntryForm.svelte';
    import MyDayCard from './MyDayCard.svelte';
    import DailyHabitsCard from './DailyHabitsCard.svelte';

    let timeEntryForm: TimeEntryForm;
    let taskForm: TaskForm;
    let metricsForm: DailyMetricsForm;
    let habitForm: HabitForm;

</script>

<TaskForm bind:this={taskForm}/>
<TimeEntryForm bind:this={timeEntryForm}/>
<HabitForm bind:this={habitForm} />
<DailyMetricsForm bind:this={metricsForm}/>

<GreetingCard />
<MyDayCard openTimeEntryForm={() => timeEntryForm.open()} openMetricsForm={() => metricsForm.open()} />
<DailyHabitsCard openHabitsForm={() => habitForm.open() } />
