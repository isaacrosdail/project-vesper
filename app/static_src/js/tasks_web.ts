import * as d3 from 'd3';

import { contextMenu } from './shared/ui/context-menu';
import { apiRequest, routes } from './shared/services/api';
import { confirmationManager } from './shared/ui/modal-manager';
import { makeToast } from './shared/ui/toast';


interface TaskNode {
    id: number;
    x: number;
    y: number;
    name: string;
    due_date: string | null;
    is_done: boolean;
    is_frog: boolean;
    priority: string;
}

interface TaskLink {
    subtask: number;
    supertask: number;
}

const height = window.innerHeight;
const width = window.innerWidth;
const nodeRadius = 40;

const color = d3.scaleOrdinal() // specify our own color mapping here so priorities are coded intuitively
    .domain(["LOW", "MEDIUM", "HIGH"])
    .range(["#42af46", "#FFC107", "#d2352a"]);


let pendingSource: number | null = null;


// TODO: Look into incremental diffs to render on adding/removing nodes.
class CanvasManager {
    private width: number;
    private height: number;
    private nodeRadius: number;
    private nodes: TaskNode[];
    private links: TaskLink[];
    private nodesMap: Map<number, TaskNode>;
    private svg!: any;
    private nodesContainer!: any;
    private linksContainer!: any;
    private zoomContainer!: any;

    constructor(height: number, width: number, nodeRadius: number, nodes: TaskNode[], links: TaskLink[]) {
        this.height = height;
        this.width = width;
        this.nodeRadius = nodeRadius;

        this.nodes = nodes;
        this.links = links;
        this.nodesMap = new Map(
            this.nodes.map(node => [node.id, node])
        )
    }

    // Create SVG containers, define markers, init d3.zoom
    init() {
        this.svg = d3.select('#web')
            .append("svg")
            .attr("viewBox", [0, 0, this.width, this.height])
            .attr("background", "var(--bg)")

        this.svg
            .append("svg:defs") // one-time definition for markers?
            .selectAll("markers")
            .data(["end"])
            .enter()
            .append("svg:marker") // this adds in the arrows
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("fill", "red")
            .attr("refX", 30)
            .attr("refY", 0)
            .attr("markerWidth", 20)
            .attr("markerHeight", 20)
            .attr("orient", "auto-start-reverse")
            .append("svg:path")
            .attr("d", "M0,-5L10,0L0,5");

        this.zoomContainer = this.svg.append("g")

        const zoom = d3.zoom()
            .scaleExtent([0.7, 2]) // defines scale factor range allowed
            .on("zoom", (event) => {
                this.zoomContainer.attr("transform", event.transform)
            })
        this.svg.call(zoom)

        this.linksContainer = this.zoomContainer.append("g")
            .attr("class", "links")

        // make group for all nodes
        this.nodesContainer = this.zoomContainer.append("g")
            .attr("stroke-width", 1.5) // TODO: remove?
    }

    // Rebuilds nodesMap and prunes links to match current nodes
    recomputeDerivedState() {
        this.nodesMap = new Map(this.nodes.map(node => [node.id, node]));
        // Keep only links where both ends still exist in nodesMap
        this.links = this.links.filter(
            link => this.nodesMap.has(link.subtask) && this.nodesMap.has(link.supertask)
        )
    }

    private onDragStart = (event, d) => {
        d3.select(event.sourceEvent.currentTarget).select("circle")
            .attr("fill", "red")
            .attr("cursor", "grabbing");
    }

    updateNodes() {
        const capturedThis = this; // capture 'this'
        // initial graph of nodes setup?
        this.nodesContainer.selectAll("g.node") // g.node = a single node, in full (circle+text)
            .data(this.nodes, d => d.id)
            .join(
                enter => {
                    const nodeGroup = enter.append("g")
                        .attr("class", "node")
                        .attr("data", d => `id-${d.id}`) // represents id from node arr
                        .attr("transform", d => `translate(${d.x}, ${d.y})`);

                    nodeGroup.append("circle")
                        .attr("r", this.nodeRadius)
                        .attr("cx", 0)
                        .attr("cy", 0)
                        .attr("fill", d => color(d.priority));

                    nodeGroup.append("text")
                        .attr("dy", 20)
                        .attr("fill", "var(--text-muted)") // TODO: move to CSS class!
                        .attr("text-anchor", "middle")
                        .text(d => d.name);

                    // Set up drag handlers
                    nodeGroup.call(d3.drag()
                        // .on("start", function(event, d) {
                        //     d3.select(this).select("circle")
                        //         .attr("fill", "red")
                        //         .style("cursor", "grabbing");
                        // })
                        .on("start", this.onDragStart)
                        .on("drag", function(event, d) {
                            d.x = event.x;
                            d.y = event.y;
                            d3.select(this).attr("transform", `translate(${d.x}, ${d.y})`);

                            capturedThis.updateLinks(); // update visual links
                        })
                        .on("end", function(event, d) {
                            d3.select(this).select("circle")
                                .attr("fill", d => color(d.priority))
                                .style("cursor", "grab")
                        })
                    )
                    .on('dblclick', function(event, d) {
                        event.stopPropagation();
                        // A. pendingSource isn't null, but this is the same node
                        if (pendingSource !== null && pendingSource === d.id) {
                            pendingSource = null;
                            d3.selectAll("circle").attr("opacity", "1.0");
                            return;
                        }
                        // B. If pendingSource, then link mode active -> set THIS node as the "link to this" one?
                        if (pendingSource !== null) {
                            // then this node's id is the one to be linked to the pendingSource's id?
                            const url = routes.tasks.task_links.collection;
                            const subtaskId = pendingSource; // capture before clearing
                            apiRequest('POST', url, { subtask_id: subtaskId, supertask_id: d.id }, {
                                onSuccess: (responseData) => {
                                    capturedThis.addLink(subtaskId, d.id);
                                    pendingSource = null; // revert out of link mode
                                    d3.selectAll("circle").attr("opacity", "1.0");
                                },
                                onFailure: (responseData) => {
                                    pendingSource = null;
                                    makeToast(responseData.message, 'error');
                                }
                            })
                            return
                        }
                        // B. If pendingSource is null -> set this node as pending source and dim all other nodes
                        pendingSource = d.id;
                        // dim all other nodes
                        d3.selectAll("circle").attr("opacity", "0.5")
                        d3.select(this).select("circle").attr("opacity", "1.0")
                    })
                    .on('contextmenu', (event, d) => {
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
                                        const url = routes.tasks.tasks.item(d.id);
                                        apiRequest('DELETE', url, null, {
                                            onSuccess: () => {
                                                // Filter out the el in nodes whose id === d.id
                                                this.nodes = this.nodes.filter(n => n.id !== d.id);

                                                this.recomputeDerivedState();
                                                this.updateNodes();
                                                this.updateLinks();
                                            }
                                        })
                                    }
                                }
                            ]
                        })
                    })
                    // ALWAYS: bring hovered node to opacity 1
                    // Only when no pendingSource: dim all others first.
                    .on('mouseenter', function(event, d) {
                        if (pendingSource !== null) {
                            d3.select(this).select("circle").attr("opacity", "1");
                            return;
                        }
                        // TODO: Somehow change the color of the links of adjacents to --accent-subtle too?

                        // On hover of this node:
                        // 1. Dim all nodes (~0.5 opacity)
                        // 2. Then put this node + neighbor nodes back to 1.0 opacity
                        d3.selectAll("circle").attr("opacity", "0.5")
                        // then...also change all adjacent nodes
                        // so ALSO change the color attr of any nodes with a link entry with 'this' node's id in it?
                        const matches = capturedThis.links.filter(
                            link => link.subtask === d.id || link.supertask === d.id
                        )
                        // for each matching link, get the _other_ node's ID
                        // if this node is the subtask in the link   -> grab the supertask ID
                        // if this node is the supertask in the link -> grab the subtask ID
                        const neighborIds = matches.map(link =>
                            link.subtask === d.id ? link.supertask : link.subtask
                        )

                        d3.select(this).select("circle").attr("opacity", "1.0")
                        d3.selectAll("circle").filter(n => neighborIds.includes(n.id))
                            .attr("opacity", "1.0")
                    })
                    .on('mouseleave', function(event, d) {
                        // Three cases:
                        if (pendingSource !== null) {
                            // 1. Link mode, leaving a non-source node: set just this node back to 0.5
                            if (d.id !== pendingSource) {
                                d3.select(this).select("circle").attr("opacity", "0.5")
                            }
                            // 2. Link mode, leaving the source node: do nothing, stays at 1.0
                            return;
                        }
                        // 3. Normal mode: restore all to 1.0
                        d3.selectAll("circle").attr("opacity", "1.0")
                    });

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
    }

    // Create / Update (visually) links between nodes #3f3f3f #1e1e1e
    updateLinks() {
        const applyCoords = (sel: any) => sel
            .attr("x1", d => this.nodesMap.get(d.subtask)!.x)
            .attr("y1", d => this.nodesMap.get(d.subtask)!.y)
            .attr("x2", d => this.nodesMap.get(d.supertask)!.x)
            .attr("y2", d => this.nodesMap.get(d.supertask)!.y);

        this.linksContainer.selectAll("line")
            .data(this.links)
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

    }

    // TODO: These two will need to guard against duplicate IDs
    // Shouldn't be dupes but just in case?
    // Adds a new node to canvas state and triggers a full re-render
    addNode({ id, name }) {
        // Default initial position
        const initialPos = { x: 30, y: 30 };
        this.nodes.push({
            id, x: initialPos.x, y: initialPos.y, name
        })

        // recompute derived state
        this.recomputeDerivedState();
        this.updateNodes();
        this.updateLinks();
    }

    // Adds a link between two existing node IDs and updates link visuals
    addLink(fromID, toID) {
        this.links.push({
            subtask: fromID, supertask: toID
        })
        this.recomputeDerivedState();
        this.updateLinks();
    }
}

export async function init() {
    const url = routes.tasks.tasks.collection;
    const response = await apiRequest('GET', url, null);

    // Circular layout formula for nodes' starting positions. center of viewport?
    const [center_x, center_y] = [width/2, height/2];
    const num_nodes = response.data.length;
    const layoutRadius = Math.min(width, height) * 0.35;
    const tasksWithPositions: TaskNode[] = response.data.map((task: TaskNode, i: number) => ({
        ...task,
        x: center_x + layoutRadius * Math.cos((2 * Math.PI * i) / num_nodes),
        y: center_y + layoutRadius * Math.sin((2 * Math.PI * i) / num_nodes),
    }))

    const links = response.data.flatMap(task =>
        task.supertasks.map(supertaskId => ({
            subtask: task.id,
            supertask: supertaskId
        }))
    )

    const canvas = new CanvasManager(height, width, nodeRadius, tasksWithPositions, links);
    canvas.init();
    canvas.updateNodes();
    canvas.updateLinks();

    // TODO: Right spot for this?
    document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape' || pendingSource === null) {
            return;
        }
        pendingSource = null;
        d3.selectAll("circle").attr("opacity", "1.0");
    })
}
