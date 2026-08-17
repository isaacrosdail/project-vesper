<script lang="ts">
    import { SvelteMap } from 'svelte/reactivity';
    import { createLink, subtasksOf, tasksState } from './tasksState.svelte';
    import type { Attachment } from 'svelte/attachments';
    import * as d3 from 'd3';
    import type { TaskRead } from '../apiTypes';
    import { kahns } from './graph';
    import { addToast } from '../shared/components/Toaster.svelte';
    import { withinHops } from './graph';
    import { Temporal } from 'temporal-polyfill';
    import { fmtDate } from '../shared/datetime';
    import { createHotkey } from '@tanstack/svelte-hotkeys';

    createHotkey('Escape', cancelLinking, () => ({
        enabled: canvasState.mode === 'linking',
        meta: { name: 'Cancel linking mode' },
    }));
    // TODO:
    // 0. Replace the circle init layout with a proper "tree sort" esque layout
    // 1. Add lasso to select + move multiple nodes
    // 2. Make the links have a value representing "completion estimate" somehow?
    //     Then we can use Dijkstras / other graph algos to find shortest paths? thatd be neato
    // 3. For

    let { onOpenMenu }: {
        onOpenMenu: (id: number, x: number, y: number, extra: any[]) => void;
    } = $props();

    type CanvasMode = { mode: 'idle' } | { mode: 'linking'; sourceId: number };
    let canvasState: CanvasMode = $state<CanvasMode>({ mode: 'idle' });

    // drag -> move it -> attachment DONE
    // wheel -> zoom -> attachment   DONE
    // esc -> cancel linking mode
    // zoom pass 1.5 -> reveal labels/details
    // space/d with a node hovered -> toggle complete
    // L with a node hovered -> enter linking from hoveredId
    //

    let hoveredId = $state<number | null>(null);

    let legendOpen = $state<boolean>(false);

    const neighborIds: Map<number, number> = $derived.by(() => {
        return hoveredId === null ? new Map() : withinHops(adjMap, hoveredId, 1);
    });
    // Map of sets shape: each time tasks changes, make an adjacency map
    const adjMap: Map<number, Set<number>> = $derived.by(() => {
        const myMap = new Map<number, Set<number>>();
        // for each task id, get its immediate subtasks and add to set?
        tasksState.tasks.forEach((t) => {
            const mySet = new Set<number>([...t.supertasks, ...t.subtasks]);
            myMap.set(t.id, mySet);
        });
        return myMap;
    });

    const zoomedNodeId = $derived.by(() => {
        if (zoomTransform.k <= 1.5) return null;
        const [invX, invY] = zoomTransform.invert([VIEW / 2, VIEW / 2]);
        let best: { id: number; dist: number } = { id: -1, dist: Infinity };
        for (const t of tasksState.tasks) {
            const p = posOf(t.id);
            const dist = (p.x - invX) ** 2 + (p.y - invY) ** 2;
            if (dist < best.dist) best = { id: t.id, dist };
        }
        return best.dist < 50_000 ? best.id : null;
    });

    function initiateLinking(id: number) {
        canvasState = { mode: 'linking', sourceId: id };
    }
    function cancelLinking() {
        canvasState = { mode: 'idle' };
    }
    async function completeLink(t: TaskRead) {
        if (canvasState.mode !== 'linking') throw new Error('Error: Somehow wasn\'t in linking mode?');
        const subId = canvasState.sourceId;
        // Verify acyclic
        const proposedLinks = [...links, { subtask_id: subId, supertask_id: t.id }];
        if (
            kahns(
                tasksState.tasks.map((t) => t.id),
                proposedLinks.map((l) => [l.supertask_id, l.subtask_id]),
            ) === null
        ) {
            addToast(
                'Cannot link',
                'Would create a circular dependency in task completion order',
                'error',
            );
            return;
        }
        try {
            await createLink(subId, t.id);
        } catch (err) {
            //
        } finally {
            canvasState = { mode: 'idle' };
            // node-hover-dim here too?
        }
    }

    // Will store the view transform:
    // consists of k (scale), plus x,y (pan offset)
    let zoomTransform = $state(d3.zoomIdentity); // zoomIdentity = the "no zoom yet" transform

    // d3.zoom() returns a _behavior_: d3's lingo for "a fn with configuration methods hanging off it"
    function zoomable(node: SVGSVGElement) {
        const zoom = d3
            .zoom<SVGSVGElement, unknown>()
            .scaleExtent([0.7, 2])
            .on('zoom', (e) => {
                zoomTransform = e.transform;
            });
        d3.select(node).call(zoom); // install

        return () => d3.select(node).on('.zoom', null); // cleanup
    }

    // Factory -> called in the template as draggable(t)
    // Closes over t so the drag callbacks know which task they belong to.
    function draggable(t: TaskRead): Attachment<SVGGElement> {
        // Attachment -> Svelte calls it when the <g> mounts
        return (node) => {
            d3.select(node).call(
                d3
                    .drag<SVGGElement, unknown>()
                    .subject(() => posOf(t.id))
                    .on('drag', (event) => positions.set(t.id, { x: event.x, y: event.y })),
            );
            // Cleanup -> Svelte calls it when the <g> unmounts
            // '.drag' = every listener in the drag namespace
            // passing null removes them
            return () => d3.select(node).on('.drag', null);
        };
    }
    const NODE_RADIUS = 40;
    const arcGen = d3
        .arc<{ startAngle: number; endAngle: number }>()
        .innerRadius(NODE_RADIUS + 2)
        .outerRadius(NODE_RADIUS + 4);

    // Bound to clientWidth/Height in .canvas-wrap div
    let width = $state(0);
    let height = $state(0);

    const positions = new SvelteMap<number, { x: number; y: number }>();
    const VIEW = 1000; // defines... ??!???
    function posOf(id: number) {
        const angle = (id * 2.399963) % (2 * Math.PI);  // golden angle, stable per id
        return positions.get(id) ?? {
            x: VIEW / 2 + VIEW * 0.35 * Math.cos(angle),
            y: VIEW / 2 + VIEW * 0.35 * Math.sin(angle),
        }
    }

    const links = $derived(
        tasksState.tasks.flatMap((task) =>
            task.supertasks.map((supertaskId) => ({
                subtask_id: task.id,
                supertask_id: supertaskId,
            })),
        ),
    );

    function dueProgress(from: string, to: string, now = Temporal.Now.instant()) {
        const start = Temporal.Instant.from(from);
        const end = Temporal.Instant.from(to);
        const remaining = now.until(end);
        const total = start.until(end).total('milliseconds');
        const elapsed = start.until(now).total('milliseconds');
        const frac = Math.min(elapsed / total, 1);
        const daysLeft = Math.ceil(remaining.total('days'));
        return { frac, daysLeft };
    }

    function dueDetailsView(t: TaskRead) {
        if (t.completed_at) return `Completed: ${fmtDate(t.completed_at)}`;
        if (!t.due_datetime) return '';
        const { daysLeft } = dueProgress(t.created_at, t.due_datetime);
        const display = daysLeft > 0 ? `${daysLeft}d left` : `${Math.abs(daysLeft)}d overdue`;
        return `Due: ${fmtDate(t.due_datetime)} (${display})`;
    }
</script>

<!-- <svelte:window
    onkeydown={(e) => {
        if (e.key === 'Escape' && canvasState.mode === 'linking') cancelLinking();
    }} /> -->

<div class="canvas-wrap" bind:clientWidth={width} bind:clientHeight={height}>
    <details class="legend" bind:open={legendOpen}>
        <summary class="legend-title">Legend</summary>
        <div class="legend-row">
            <svg viewBox="0 0 24 20"><use href="#badge-priority-low" /></svg>
            <span>Low priority</span>
        </div>
        <div class="legend-row">
            <svg viewBox="0 0 24 20"><use href="#badge-priority-medium" /></svg>
            <span>Medium priority</span>
        </div>
        <div class="legend-row">
            <svg viewBox="0 0 24 20"><use href="#badge-priority-high" /></svg>
            <span>High priority</span>
        </div>
        <div class="legend-row">
            <svg viewBox="0 0 24 24"><use href="#badge-priority-frog" /></svg>
            <span>Frog</span>
        </div>
        <div class="legend-row">
            <svg viewBox="0 0 24 24">
                <circle class="legend-ring" cx="12" cy="12" r="9" pathLength="100" />
            </svg>
            <span>Time until due</span>
        </div>
        <div class="legend-row">
            <svg viewBox="0 0 24 24"
                ><use href="#check-icon" width="18" height="18" x="3" y="3" /></svg>
            <span>Completed</span>
        </div>
        <div class="legend-row">
            <svg viewBox="0 0 24 24"
                ><line class="legend-link" x1="2" y1="12" x2="22" y2="12" /></svg>
            <span>Dependency path (hover)</span>
        </div>
        <div class="legend-row">
            <span class="legend-count">2/5</span>
            <span>Subtasks done</span>
        </div>
    </details>
    <!-- TODO: remove debug -->
    <span>Linking mode: {canvasState.mode}</span>
    <svg viewBox={`0 0 1000 1000`} {@attach zoomable}>
        <!-- guard against split-second initial render -->
        {#if width > 0}
            <g
                transform={String(zoomTransform)}>
                <!-- // class:node-focused={canvasState.mode === 'idle' && hoveredId !== null -->
                {#each links as l (`${l.subtask_id}-${l.supertask_id}`)}
                    {@const sub = posOf(l.subtask_id)}
                    {@const sup = posOf(l.supertask_id)}
                    {@const dSub = neighborIds.get(l.subtask_id)}
                    {@const dSup = neighborIds.get(l.supertask_id)}
                    {@const deg = Math.atan2(sup.y - sub.y, sup.x - sub.x) * (180 / Math.PI)}
                    <!-- Math.abs(a -b) <- rims sit level (diff 0), spokes (diff 1)? generalizes too: at n=3, the (3,2) pairs light up too? -->
                    <g
                        class:highlighted={dSub !== undefined &&
                            dSup !== undefined &&
                            Math.abs(dSub - dSup) === 1}
                        style:--n-away={dSub !== undefined && dSup !== undefined
                            ? Math.max(dSub, dSup)
                            : 0}>
                        <line class="link-line" x1={sub.x} x2={sup.x} y1={sub.y} y2={sup.y} />
                        <polygon
                            class="link-chevron"
                            points="0,-5 10,0 0,5"
                            transform={`translate(${(sub.x + sup.x) / 2}, ${(sub.y + sup.y) / 2}) rotate(${deg})`} />
                    </g>
                {/each}
                {#each tasksState.tasks as t (t.id)}
                    {@const hovering = canvasState.mode === 'idle' && hoveredId !== null}
                    {@const inHood = neighborIds.has(t.id)}
                    {@const pos = posOf(t.id)}
                    <g
                        role="none"
                        {@attach draggable(t)}
                        onclick={() => {
                            if (canvasState.mode !== 'linking') return;
                            if (t.id === canvasState.sourceId) {
                                cancelLinking();
                            } else if (canvasState.mode === 'linking') {
                                completeLink(t);
                            }
                        }}
                        onmouseenter={() => (hoveredId = t.id)}
                        onmouseleave={() => (hoveredId = null)}
                        oncontextmenu={(e) => {
                            e.preventDefault();
                            onOpenMenu(t.id, e.clientX, e.clientY, [
                                { label: 'Add link to...', action: () => initiateLinking(t.id) }
                        ])}}
                        class="node"
                        class:node-done={t.is_done}
                        class:node-zoomed={t.id === zoomedNodeId}
                        class:node-focused={hovering && inHood}
                        class:node-hover-dim={canvasState.mode === 'linking'
                            ? t.id !== canvasState.sourceId && t.id !== hoveredId
                            : hovering && !inHood}
                        transform={`translate(${pos.x}, ${pos.y})`}>
                        {#if t.due_datetime !== null && !t.is_done}
                            {@const { frac } = dueProgress(t.created_at, t.due_datetime)}
                            <path
                                d={arcGen({ startAngle: 0, endAngle: frac * 2 * Math.PI })}
                                style:fill={`color-mix(in oklab, var(--clr-error) ${Math.round(Math.max(0, frac) * 100)}%, var(--clr-success))`} />
                        {/if}
                        <circle class="node-circle" r={NODE_RADIUS}></circle>
                        <text class="node-text node-label" y="56">
                            {t.name.length > 12 ? `${t.name.slice(0, 12)}...` : t.name}
                        </text>
                        {#if t.id === zoomedNodeId}
                            <text class="node-text node-label-full" y="56">
                                {t.name}
                            </text>
                        {/if}
                        <use
                            href={`#badge-priority-${t.priority}`}
                            class="icon"
                            x="-10"
                            y={t.subtasks.length ? -18 : -10}
                            width="20"
                            height="20"></use>
                        {#if t.subtasks.length}
                            <text class="node-text subtask-count" y="24">
                                <tspan>{subtasksOf(t).filter((st) => st.is_done).length} /</tspan>
                                <tspan>{t.subtasks.length}</tspan>
                            </text>
                        {/if}
                        {#if t.is_done}
                            <circle class="is-done-circle" r="12" cx="30" cy="30"></circle>
                            <use
                                class="is-done-icon"
                                href="#check-icon"
                                width="15"
                                height="15"
                                x="22.5"
                                y="22.5"></use>
                        {/if}
                        <text class="node-text node-details">
                            <tspan x="50" dy="0">{t.name}</tspan>
                            <tspan x="50" dy="18">{dueDetailsView(t)}</tspan>
                        </text>
                    </g>
                {/each}
            </g>
        {/if}
    </svg>
</div>

<style>
    /* node, link */
    /* D3 drag handlers cover changing from grab -> grabbing -> grab */
    .node:hover {
        cursor: grab;
    }

    .canvas-wrap {
        position: relative;
        height: 75dvh;
    }
    svg {
        width: 100%;
        height: 100%;
        display: block;
    }
    .legend {
        position: absolute;
        top: var(--space-sm);
        right: var(--space-sm);
        display: grid;
        gap: var(--space-xs);
        padding: var(--space-sm);
        background: var(--surface-1);
        border: var(--border-default);
        border-radius: var(--border-radius-mild);
        font-size: var(--font-size-sm);
        color: var(--text-muted);
    }
    .legend-title {
        color: var(--text);
        cursor: pointer;
        user-select: none;
    }
    .legend-row {
        display: flex;
        align-items: center;
        gap: var(--space-xs);
    }
    .legend-row svg {
        width: 18px;
        height: 18px;
        flex-shrink: 0;
        fill: currentColor;
    }
    .legend-ring {
        fill: none;
        stroke: #e08600;
        stroke-width: 3;
        stroke-dasharray: 65 35; /* partial arc, ~65% elapsed */
        transform: rotate(-90deg);
        transform-origin: center;
    }
    .legend-link {
        stroke: var(--accent-strong);
        stroke-width: 2.5;
    }
    .legend-count {
        width: 18px;
        text-align: center;
        flex-shrink: 0;
    }

    .subtask-count {
        text-anchor: middle;
    }
    .is-done-circle {
        fill: var(--surface-1);
    }
    .is-done-icon {
        fill: var(--clr-success);
    }

    /* Contrast for all text for nodes */
    .node-text {
        paint-order: stroke;
        stroke: var(--bg);
        stroke-width: 3px;
        stroke-linejoin: round;
        transition: opacity 0.2s ease;
        pointer-events: none;
    }

    .node-details {
        fill: var(--text-muted);
        text-anchor: start;
        pointer-events: none;
        opacity: 0;
    }

    .node-circle {
        fill: var(--node-color);
    }
    .highlighted .link-line,
    .highlighted .link-chevron {
        stroke-width: calc((5 - var(--n-away)) * 0.5px);
        stroke: oklch(0.5438 0.191 267.01 / calc(1.25 - var(--n-away) * 0.35));
    }
    .link-line {
        stroke: #4e4e4e;
    }
    .link-chevron {
        fill: var(--accent-strong);
    }
    .node-label,
    .node-label-full {
        text-anchor: middle;
    }
    .node-label-full {
        opacity: 0;
    }

    .node-hover-dim .node-circle,
    .node-hover-dim .node-label {
        opacity: 0.5;
    }

    /* Shrink by ~25% somehow? cant just use transform tho
        some kind of animation, for extra credit
    */
    .node-done {
        opacity: 0.4;
    }

    .node-focused .node-label {
        opacity: 0;
    }
    .node-focused .node-label-full {
        opacity: 1;
    }

    /* Shows details + swaps truncated/full labels */
    .node-zoomed .node-label {
        opacity: 0;
    }
    .node-zoomed .node-label-full {
        opacity: 0;
    }
    .node-zoomed .node-details {
        opacity: 1;
    }
</style>
