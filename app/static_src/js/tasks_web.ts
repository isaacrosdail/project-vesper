import * as d3 from 'd3';

import { Queue } from './data_structures';
import { getJSInstant } from './shared/datetime';
import { api } from './shared/services/api';
import { contextMenu } from './shared/ui/context-menu';
import { confirmationManager } from './shared/ui/modal-manager';
import { makeToast } from './shared/ui/toast';
import { Task } from './types';


interface TaskNode extends Task {
    x: number;
    y: number;
}

interface TaskLink {
    subtask: number;
    supertask: number;
}

type CanvasMode =
    | { mode: 'idle' }
    | { mode: 'linking'; sourceId: number; };


const color = d3.scaleOrdinal<string, string>() // specify our own color mapping here so priorities are coded intuitively
    .domain(["low", "medium", "high"])
    .range(["var(--clr-success)", "#f5ee19", "var(--clr-error)"]);


function kahns(nodes: TaskNode[], links: TaskLink[]): number[] | null {
    // 1. build in-degree count for every node
    const inDegree = new Map<number, number>();

    nodes.forEach(node => inDegree.set(node.id, 0));

    // Adjacency map: parent (supertask) -> children (subtask)
    // This turns later O(V*E) lookups into O(1)
    const adjMap = new Map<number, number[]>();
    links.forEach(link => {
        // Set in-degree counts for each:
        inDegree.set(link.subtask, inDegree.get(link.subtask)! + 1);

        // Build up adjacency map
        if (!adjMap.has(link.supertask)) {
            adjMap.set(link.supertask, [])
        }
        adjMap.get(link.supertask)!.push(link.subtask)
    })

    // 2. Collect all nodes with in-degree of 0 into queue
    const queue = new Queue<number>();
    inDegree.forEach((degree, nodeId) => {
        if (degree === 0) queue.enqueue(nodeId);
    });

    // 3. While queue isn't empty: pull a node, add to result, decrement in-degree of all its neighbors.
    // If any neighbor hits 0, add to queue.
    const result: number[] = []
    while (queue.size > 0) {
        const nodeId = queue.dequeue();
        result.push(nodeId);

        // Decrement degree of all its neighbors: its children (subtasks) now have one fewer blocker?
        (adjMap.get(nodeId) ?? []).forEach(l => {
            inDegree.set(l, inDegree.get(l) - 1); // decrement each one's inDegree in map
            if (inDegree.get(l) === 0) {
                queue.enqueue(l)
            }
        })
    }
    // Cycle
    if (result.length < nodes.length) {
        return null;
    }
    return result
}



// TODO: Look into incremental diffs to render on adding/removing nodes.
class CanvasManager {
    #width = window.innerWidth;
    #height = window.innerHeight;
    #state: CanvasMode = { mode: 'idle' };
    #nodes: TaskNode[];
    #links: TaskLink[];
    #nodeRadius = 40;
    #nodesMap: Map<number, TaskNode>;
    #svg!: d3.Selection<SVGSVGElement, unknown, HTMLElement, unknown>;
    #nodesContainer!: d3.Selection<SVGGElement, unknown, HTMLElement, unknown>;
    #linksContainer!: d3.Selection<SVGGElement, unknown, HTMLElement, unknown>;
    #zoomContainer!: d3.Selection<SVGGElement, unknown, HTMLElement, unknown>;
    #arcGen;

    constructor(tasks: Task[], links: TaskLink[]) {
        // Circular layout formula for nodes' starting positions. center of viewport?
        const centerX = this.#width  / 2;
        const centerY = this.#height / 2;
        const num_nodes = tasks.length;
        const layoutRadius = Math.min(this.#width, this.#height) * 0.35;

        this.#nodes = tasks.map((task, i) => ({
            ...task,
            x: centerX + layoutRadius * Math.cos((2 * Math.PI * i) / num_nodes),
            y: centerY + layoutRadius * Math.sin((2 * Math.PI * i) / num_nodes),
        }));
        this.#links = links;
        this.#nodesMap = new Map(this.#nodes.map(node => [node.id, node]));

        // arcGen here? for due_date arcs
        // d3.arc() -> innerRadius = 42, outerRadius = 46 gives a thin ring around an r=40 node
        // 0 -> 2pi: start angle at 0 (top), end angle is how full arc should be, dictated at usage sites
        this.#arcGen = d3.arc().innerRadius(this.#nodeRadius + 2).outerRadius(this.#nodeRadius + 4);
    }

    // Create SVG containers, define markers, init d3.zoom
    init() {
        this.#svg = d3.select('#web').append("svg")
            .attr("viewBox", [0, 0, this.#width, this.#height])
            .attr("background", "var(--bg)")

        // TODO: Add attribution: from heroicons "check" svg
        this.#svg.append("defs")
            .append("symbol")
            .attr("id", "check-icon")
            .attr("viewBox", "0 0 24 24")
            .append("path")
            .attr("d", "m4.5 12.75 6 6 9-13.5")
            .attr("stroke", "var(--clr-success)")
            .attr("stroke-width", 4.5)
            .attr("stroke-linecap", "round")
            .attr("stroke-linejoin", "round")
            .attr("fill", "none")

        const gGridData = this.#svg.append("g")

        // for(let x = 0; x < this.#width; x += 50) {
        //     // vertical
        //     gGridData.append("line")
        //         .attr("x1", x).attr("x2", x)
        //         .attr("y1", 0).attr("y2", this.#height)
        //         .attr("stroke", "red")
        //         .attr("stroke-opacity", 0.25)

        //     // horizontal
        //     gGridData.append("line")
        //         .attr("x1", 0).attr("x2", this.#width) // same as vertical, just flip x's for y's, vice versa
        //         .attr("y1", x).attr("y2", x)
        //         .attr("stroke", "red")
        //         .attr("stroke-opacity", 0.25)
        // }

        
        this.#zoomContainer = this.#svg.append("g")
        const gGridView = this.#zoomContainer.append("g")
        // Loop?
        // for(let x = 0; x < this.#width; x += 50) {
        //     // vertical
        //     gGridView.append("line")
        //         .attr("x1", x)
        //         .attr("x2", x)
        //         .attr("y1", 0)
        //         .attr("y2", this.#height)
        //         .attr("stroke", "cyan")
        //         .attr("stroke-opacity", 0.25)

        //     // horizontal
        //     gGridView.append("line")
        //         .attr("x1", 0)
        //         .attr("x2", this.#width)
        //         .attr("y1", x)
        //         .attr("y2", x)
        //         .attr("stroke", "cyan")
        //         .attr("stroke-opacity", 0.25)
        // }

        const zoom = d3.zoom()
            .scaleExtent([0.7, 2]) // defines scale factor range allowed
            .on("zoom", (event, d) => {
                this.#zoomContainer.attr("transform", event.transform)
                const {k, x, y} = event.transform;
                // Viewport center is (500, 400) : half of our width/height
                // this.#width/2 & this.#height/2 -> Screen/viewport center (middle of browser window)
                // event.transform.invert() converts that screen point back to data space, giving us data-space coords of whatever
                // is currently at the center of our view
                const [invX, invY] = event.transform.invert([this.#width/2, this.#height/2])
                // so we have this.#nodes with their data-space x,y
                // And we want to find "Which node has the smallest dist between invX,invY and the node?"
                // (node.x - invX)^2 + (node.y - invY)^2 = distance^2
                // If a node is at (100, 100) and we're looking at (102, 100), the dist is 2?
                // And since we just care about "closest" not "actual value", we can skip the ^2 part
                // Since if dist^2 A < dist^2 < B, then dist A < dist B, too.
                // Show text?
                if (event.transform.k > 1.5) {
                    const closest = this.#nodes.reduce((acc, node)=> {
                        // Want to return: node => { node, dist } where thats the node
                        // with best dist (lowest) and the dist val itself (for further comparing
                        // without recalculating "last dist" each time?)
                        const dist = (node.x - invX)**2 + (node.y - invY)**2 // Euclidean distance formula
                        // That's THIS nodes dist from where we're looking at
                        // Now to compare against acc.dist? return whichever is smaller
                        return acc.dist < dist ? acc : { node, dist }
                    }, { node: null, dist: Infinity })

                    d3.selectAll("g.node").classed("node-zoomed", false)
                    if (closest.dist < 50000) {
                        const thisNode = d3.select(`[data="id-${closest.node.id}"]`)
                        thisNode.classed("node-zoomed", true)
                    }
                }
                if (event.transform.k < 1.5) {
                    d3.selectAll("g.node").classed("node-zoomed", false)
                }
            })
        this.#svg.call(zoom)

        this.#linksContainer = this.#zoomContainer.append("g")
            .attr("class", "links")

        // make group for all nodes
        this.#nodesContainer = this.#zoomContainer.append("g")
            .attr("stroke-width", 1.5) // TODO: remove?

        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Escape' || this.#state.mode === 'idle') {
                return;
            }
            this.#state = { mode: 'idle' };
            d3.selectAll("g.node").classed("node-hover-dim", false)
        })
    }

    // Rebuilds nodesMap and prunes links to match current nodes
    recomputeDerivedState() {
        this.#nodesMap = new Map(this.#nodes.map(node => [node.id, node]));
        // Keep only links where both ends still exist in nodesMap
        this.#links = this.#links.filter(
            link => this.#nodesMap.has(link.subtask) && this.#nodesMap.has(link.supertask)
        )
    }

    async #handleDblClick(event: MouseEvent, d: TaskNode) {
        event.stopPropagation();
        const nodeEl = event.currentTarget as SVGGElement;
        // A. Linking mode but clicking the same node again
        if (this.#state.mode === 'linking' && this.#state.sourceId === d.id ) {
            this.#state = { mode: 'idle' };
            d3.selectAll("g.node").classed("node-hover-dim", false)
            return;
        }
        // B. Linking mode, second dblclick -> attempt to create link to this node
        if (this.#state.mode === 'linking') {
            const subtaskId = this.#state.sourceId; // capture before clearing
            // Verify acyclic with Kahn's
            const proposedLinks = [...this.#links, { subtask: subtaskId, supertask: d.id }];
            const result = kahns(this.#nodes, proposedLinks)
            if (result === null) {
                makeToast('Cannot link: would create a circular dependency in task completion order', 'error')
                this.#state = { mode: 'idle' }
                d3.selectAll("g.node").classed("node-hover-dim", false)
                return
            }

            try {
                const response = await api.taskLinks.create({ subtask_id: subtaskId, supertask_id: d.id })
                this.addLink(subtaskId, d.id)
                makeToast(response.message, 'success')
            } catch (error) {
                makeToast(error.message, 'error');
            } finally {
                this.#state.mode = 'idle';
                d3.selectAll("g.node").classed("node-hover-dim", false)
            }
            return
        }
        // C. Idle mode -> enter linking mode with this node as source
        this.#state = { mode: 'linking', sourceId: d.id };
        d3.selectAll("g.node").classed("node-hover-dim", true)
        d3.select(nodeEl).classed("node-hover-dim", false)
    }

    #handleContextMenu(event: MouseEvent, d: TaskNode) {
        event.preventDefault();
        contextMenu.create({
            position: { x: event.clientX, y: event.clientY },
            items: [
                {
                    label: 'Delete',
                    action: async () => {
                        const confirmed = await confirmationManager.show(
                            "Are you sure you want to delete this task?"
                        );
                        if (!confirmed) return;
                        await api.tasks.delete(String(d.id));
                        // Filter out the el in nodes whose id === d.id
                        this.#nodes = this.#nodes.filter(n => n.id !== d.id);

                        this.recomputeDerivedState();
                        this.updateNodes();
                        this.updateLinks();
                    }
                },
                {
                    label: 'Toggle complete',
                    action: async () => {
                        await api.tasks.toggleComplete(String(d.id), d.is_done)
                        d.is_done = !d.is_done;
                        this.recomputeDerivedState();
                        this.updateNodes();
                        makeToast('Task status update', 'success');
                    }
                }
            ]
        })
    }

    #handleMouseEnter(event: MouseEvent, d: TaskNode) {
        const nodeEl = event.currentTarget as SVGGElement;
        if (this.#state.mode === 'linking') {
            // d3.select(nodeEl).select(".node-circle").attr("opacity", "1"); // TODO class-based
            d3.select(nodeEl).classed("node-hover-dim", false)
            return;
        }
        // TODO: Somehow change the color of the links of adjacents to --accent-subtle too?
        // On hover of this node:
        // 1. Dim all nodes (~0.5 opacity)
        // 2. Then put this node + neighbor nodes back to 1.0 opacity
        // d3.selectAll(".node-circle").attr("opacity", "0.5")
        // then...also change all adjacent nodes (plus color of any nodes with a link entry with 'this' node's id in it)
        const matches = this.#links.filter(
            link => link.subtask === d.id || link.supertask === d.id
        )
        // for each matching link, get the _other_ node's ID
        // this node is the subtask in link   -> grab supertask ID
        // this node is the supertask in link -> grab subtask ID
        const neighborIds = matches.map(link =>
            link.subtask === d.id ? link.supertask : link.subtask
        )
        // show node-label-full and hide truncated text for only the nodes we care about
        d3.selectAll("g.node").classed("node-hover-dim", true)
        d3.select(nodeEl).classed("node-hover-dim", false)
        d3.select(nodeEl).classed("node-focused", true)

        // Neighbors: highlight, show full text
        const neighborGroups = d3.selectAll("g.node")
            .filter(n => neighborIds.includes(n.id));
        neighborGroups.classed("node-hover-dim", false)
        neighborGroups.classed("node-focused", true)
    }

    #handleMouseLeave(event: MouseEvent, d: TaskNode) {
        const nodeEl = event.currentTarget as SVGGElement;
        // Three cases:
        if (this.#state.mode === 'linking') {
            // 1. Link mode, leaving a non-source node: set just this node back to 0.5
            if (d.id !== this.#state.sourceId) {
                d3.select(nodeEl).classed("node-hover-dim", true)
            }
            // 2. Link mode, leaving the source node: do nothing, stays at 1.0
            return;
        }
        // 3. Normal mode: restore all to 1.0, swap back node-label-full with node-label
        d3.selectAll("g.node").classed("node-focused", false)
        d3.selectAll("g.node").classed("node-hover-dim", false)
    }

    #dueDateFraction(d: TaskNode): number {
        // Calculates the percentage of time elapsed between creation and due date, capped at 1.
        const createdAtDate = new Date(d.created_at)
        const total = new Date(d.due_date) - createdAtDate
        const elapsed = new Date() - createdAtDate
        return Math.min(elapsed / total, 1) // cap at 1
    }

    updateNodes() {
         // Capture method since 'this' binding needs to be taken by D3's drag
        const updateLinks = () => this.updateLinks();
        const dueDateFraction = (d: TaskNode) => this.#dueDateFraction(d);
        const arcGen = this.#arcGen;

        this.#nodesContainer.selectAll<SVGGElement, TaskNode>("g.node") // g.node = a single node, in full (circle+text)
            .data(this.#nodes, d => d.id)
            .join(
                enter => {
                    const nodeGroup = enter.append("g")
                        .attr("class", "node")
                        .attr("data", d => `id-${d.id}`) // represents id from node arr
                        .attr("transform", d => `translate(${d.x}, ${d.y})`);

                    // Due date "progress" arc - want behind all other elements
                    // Apply if due_date regardless of is_done status, then .each() in merged handles visibility
                    // based on current is_done
                    nodeGroup.filter(d => d.due_date !== null)
                        .append("path")
                        .attr("d", d => {
                            const dueDateFraction = this.#dueDateFraction(d)
                            return this.#arcGen({ startAngle: 0, endAngle: dueDateFraction * 2 * Math.PI })
                        })
                    .attr("fill", d => {
                        const dueDateFraction = this.#dueDateFraction(d)
                        return d3.interpolateHsl("#3cff00", "#ff0000")(dueDateFraction) // interpolate doesn't work with custom properties :(
                    })

                    // Always has circle + text ofc
                    nodeGroup.append("circle")
                        .attr("class", "node-circle")
                        .attr("r", this.#nodeRadius)
                        .attr("cx", 0).attr("cy", 0)
                        .attr("fill", "var(--node-color)")

                    // TODO: node text
                    // Always visible, truncated
                    nodeGroup.append("text")
                        .attr("dy", 20)
                        .attr("fill", "var(--text-muted)")
                        .attr("text-anchor", "middle")
                        .attr("class", "node-label")
                        .text(d => {
                            // cap around 20chars?
                            return `${d.name.slice(0, 12)}...`
                    });

                    // Hidden, appeers on zoom and hover?
                    nodeGroup.append("text")
                        .attr("dy", 20)
                        .attr("fill", "var(--text-muted)")
                        .attr("text-anchor", "middle")
                        .attr("pointer-events", "none")
                        .attr("opacity", 0)
                        .attr("class", "node-label-full")
                        .text(d => d.name)

                    // Badge background
                    nodeGroup.append("circle")
                        .attr("class", "badge-bg")
                        .attr("cx", -28)
                        .attr("cy", -28)
                        .attr("r", 14)
                        .attr("fill", "var(--bg-light)");
                    nodeGroup.append("use")
                        .attr("href", d => `#badge-priority-${d.priority}`)
                        .attr("class", "icon")
                        .attr("data-priority", d => d.priority)
                        .attr("x", -38)  // position — adjust to taste
                        .attr("y", -38)
                        .attr("width", 20)
                        .attr("height", 20);
                    // // Priority badge?
                    // nodeGroup.filter(d => d.priority !== 'low' && d.priority !== 'frog')
                    //     .append("circle")
                    //     .attr("class", "node-badge-priority")
                    //     .attr("r", 10)
                    //     .attr("cx", -28)
                    //     .attr("cy", -28)
                    //     .attr("fill", d => color(d.priority))

                    // // Frog badge
                    // nodeGroup.filter(d => d.priority === 'frog')
                    //     .append("text")
                    //     .attr("class", "node-badge-frog")
                    //     .attr("x", -28)
                    //     .attr("y", -28)
                    //     .attr("font-size", "18px")
                    //     .attr("text-anchor", "middle")
                    //     .text("🐸");

                    // is_done -> apply check mark visibility none
                    // opacity dip + check mark visibility is then dictated in the post-join merge section?
                    nodeGroup.append("use")
                        .attr("href", "#check-icon")  //from defs
                        .attr("visibility", "hidden")
                        .attr("class", "node-checkmark")
                        .attr("width", 35)
                        .attr("height", 35)
                        .attr("x", -15)
                        .attr("y", -15)

                    // TODO: Detailed view text
                    const detailText = nodeGroup.append("text")
                        .attr("class", "node-details")
                        .attr("opacity", 0)
                    
                    detailText.append("tspan")
                        .attr("x", 50).attr("dy", 0)
                        .text(d => d.name)

                    detailText.append("tspan")
                        .attr("x", 50).attr("dy", 18)
                        .text(d => {
                            const elapsed = new Date() - new Date(d.created_at)
                            const total = new Date(d.due_date) - new Date(d.created_at)
                            const daysLeft = Math.ceil((total - elapsed) / (1000 * 60 * 60 * 24))
                            const display = daysLeft > 0 ? `${daysLeft}d left` : `${Math.abs(daysLeft)}d overdue`
                            const dueDate = d.due_date
                                ? `Due: ${d.due_date.slice(5,10)} (${display})`
                                : ``
                            return dueDate
                        })

                    // Set up drag handlers
                    nodeGroup.call(d3.drag<SVGGElement, TaskNode>()
                        .on("start", function(_event, _d) {
                            d3.select(this).select(".node-circle")
                            .attr("fill", "var(--accent-strong)") // ?? idk what to make it heh
                            .style("cursor", "grabbing");
                        })
                        .on("drag", function(event, d) {
                            [d.x, d.y] = [event.x, event.y]
                            d3.select(this).attr("transform", `translate(${d.x}, ${d.y})`);
                            updateLinks();
                        })
                        .on("end", function(_event, _d) {
                            d3.select(this).select(".node-circle")
                                .attr("fill", "var(--node-color)")
                                .style("cursor", "grab");
                        })
                    )
                    .on('dblclick', (e, d) => this.#handleDblClick(e, d))
                    .on('contextmenu', (e, d) => this.#handleContextMenu(e, d))
                    .on('mouseenter', (e, d) => this.#handleMouseEnter(e, d))
                    .on('mouseleave', (e, d) => this.#handleMouseLeave(e, d));

                    return nodeGroup;
                },
                update => {
                    return update
                },
                exit => {
                    exit.remove();
                    // exit.transition().duration(300).style("opacity", 0).remove();
                }
            )
            // As soon as data updates:
            // 1. opacity for is_done task nodes lowered
            // 2. toggle visibility on checkmark SVGs
            // .attr("opacity", d => d.is_done ? 0.4 : 1)
            .each(function(d) {
                // re-compute is_done arc?
                const fraction = dueDateFraction(d)
                d3.select(this).select(".node-checkmark") // checkmark
                    .attr("visibility", d.is_done ? "visible" : "hidden")
                d3.select(this).select("path")
                    .attr("opacity", d.is_done ? 0 : 1)
                    .attr("d", arcGen({ startAngle: 0, endAngle: fraction * 2 * Math.PI }))
                // handle opacity dimming for each child element of nodeGroup individually
                // EXCEPT for the checkmark ofc
                // d3.select(this).selectAll(".node-circle").attr("opacity", d.is_done ? 0.4 : 1) // node itself + priority
                d3.select(this).classed("node-done", d.is_done)
                // d3.select(this).select(".node-label").attr("opacity", d.is_done ? 0.4 : 1)
                    // .attr("fill", d3.interpolate("var(--clr-success)", "var(--clr-error)")(fraction))
            })
    }

    // Create / Update (visually) links between nodes #3f3f3f #1e1e1e
    updateLinks() {
        const applyCoords = (sel: d3.Selection<SVGLineElement, TaskLink, SVGGElement, unknown>) => sel
            .attr("x1", d => this.#nodesMap.get(d.subtask)!.x)
            .attr("y1", d => this.#nodesMap.get(d.subtask)!.y)
            .attr("x2", d => this.#nodesMap.get(d.supertask)!.x)
            .attr("y2", d => this.#nodesMap.get(d.supertask)!.y);

        this.#linksContainer.selectAll("line")
            .data(this.#links)
            .join(
                enter => applyCoords(
                    enter.append("line")
                        .attr("stroke-linecap", "round")
                        .attr("marker-end", "url(#end)")
                        .attr("stroke", "#4e4e4e")
                ),
                update => applyCoords(update),
                exit => exit.remove()
            )

        // TODO: Study!
        const applyChevronTransform = (sel) => sel
            .attr("transform", d => {
                const source = this.#nodesMap.get(d.subtask)!;
                const target = this.#nodesMap.get(d.supertask)!;
                const midX = (source.x + target.x) / 2;
                const midY = (source.y + target.y) / 2;
                const angle = Math.atan2(target.y - source.y, target.x - source.x);
                const degrees = angle * (180 / Math.PI);
                return `translate(${midX}, ${midY}) rotate(${degrees})` // rotate to make it point in dir of line
            })

        // Chevrons?
        this.#linksContainer.selectAll(".link-chevron")
            .data(this.#links)
            .join(
                enter => applyChevronTransform(
                    enter.append("polygon")
                        .attr("class", "link-chevron")
                        .attr("points", "0,-5 10,0 0,5")
                        .attr("fill", "#4e4e4e")
                ),
                update => applyChevronTransform(update),
                exit => exit.remove()
            )

    }

    // TODO: These two will need to guard against duplicate IDs
    // Shouldn't be dupes but just in case?
    // Adds a new node to canvas state and triggers a full re-render
    addNode({ id, name }: Pick<Task, 'id' | 'name'>) {
        // Default initial position
        const initialPos = { x: 30, y: 30 };
        this.#nodes.push({
            id, x: initialPos.x, y: initialPos.y, name
        })

        // recompute derived state
        this.recomputeDerivedState();
        this.updateNodes();
        this.updateLinks();
    }

    // Adds a link between two existing node IDs and updates link visuals
    addLink(fromID: number, toID: number) {
        this.#links.push({
            subtask: fromID, supertask: toID
        })
        this.recomputeDerivedState();
        this.updateLinks();
    }
}

export async function init() {
    const param = new URLSearchParams({ include_links: 'true' })
    const response = await api.tasks.getAll(param)

    const links = response.data.flatMap(task =>
        task.supertasks.map(supertaskId => ({
            subtask: task.id,
            supertask: supertaskId
        }))
    )

    const canvas = new CanvasManager(response.data, links);
    canvas.init();
    canvas.updateNodes();
    canvas.updateLinks();
}
