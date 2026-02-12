import * as d3 from 'd3';

import { contextMenu } from './shared/ui/context-menu';
import { apiRequest, routes } from './shared/services/api';

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
const radius = 40;

const margin = { top: 20, right: 20, bottom: 30, left: 40 };
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

const debug = document.querySelector('#debug');
const color = d3.scaleOrdinal() // specify our own color mapping here so priorities are coded intuitively
    .domain(["LOW", "MEDIUM", "HIGH"])
    .range(["#42af46", "#FFC107", "#d2352a"]);

// let since we .filter on removal
let nodes = [
    {id: 1, x: 250, y: 390, name: "Plan project"},
    {id: 2, x: 360, y: 250, name: "Buy materials"},
    {id: 3, x: 145, y: 170, name: "Build thing"}
]

let links: TaskLink[] = [
    {subtask: 1, supertask: 2},
    {subtask: 1, supertask: 3},
    {subtask: 2, supertask: 3}
]

// Gist: draw a <line> from source <-> supertask, layered behind the nodes container
// So for that first link, we'd need to:
// 1. Get subtask's coords based on id
// 2. Get supertask's coords based on id
// 3. Draw a <line> from one to the other using said coords

// NOTE: Look into incremental diffs to render on adding/removing nodes.
// Also: On hover of a given node, highlight it + all nodes 1 hop away from it
class CanvasManager {
    private width: number;
    private height: number;
    private radius: number;
    private nodes: TaskNode[];
    private links: TaskLink[];
    private nodesMap: Map<number, TaskNode>;
    private svg!: any;
    private nodesContainer!: any;
    private linksContainer!: any;
    private zoomContainer!: any;

    constructor(height: number, width: number, radius: number, nodes: TaskNode[], links: TaskLink[]) {
        this.height = height;
        this.width = width;
        this.radius = radius;

        this.nodes = nodes;
        this.links = links;
        this.nodesMap = new Map(
            this.nodes.map(node => [node.id, node])
        )
    }

    init() {
        // make SVG container
        this.svg = d3.select('#web')
            .append("svg")
            .attr("viewBox", [0, 0, this.width, this.height])
            .attr("style", "outline: 5px solid red")

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
            // defines scale factor range allowed
            .scaleExtent([0.7, 2])
            .translateExtent([[0, 0], [width, height]])
            .on("zoom", (event) => {
                this.zoomContainer.attr("transform", event.transform)
            })
        this.svg.call(zoom)

        this.linksContainer = this.zoomContainer.append("g")
            .attr("class", "links")

        // make group for all nodes
        this.nodesContainer = this.zoomContainer.append("g")
            .attr("stroke", "cyan")
            .attr("stroke-width", 1.5)
            .style("outline", "1px solid red") // DEBUG

    }

    // rebuilds nodesMap and prunes links based on current nodes
    recomputeDerivedState() {
        // rebuild nodesMap
        this.nodesMap = new Map(this.nodes.map(node => [node.id, node]));
        // prune links arr
        // remove any node where EITHER subtask OR supertask's val === d.id?
        // links = links.filter(n => n.subtask !== d.id && n.supertask !== d.id)
        // since we dont wanna tie 'd' (need to pass it in) to this, lets prune links
        // based on kinda "diff'ing to nodeMap's updated contents"?
        // leverage Maps' constant lookups here
        this.links = this.links.filter(
            link => this.nodesMap.has(link.subtask) && this.nodesMap.has(link.supertask)
        )
    }

    updateNodes() {
        // Capture 'this'
        const capturedThis = this;
        // initial graph of nodes setup?
        this.nodesContainer.selectAll("g.node") // g.node = a single node, in full (circle+text)
            .data(this.nodes, d => d.name)
            .join(
                enter => {
                    // Making a single node each time here in enter
                    const nodeGroup = enter.append("g")
                        .attr("class", "node")
                        .attr("data", d => `id-${d.id}`) // represents id from node arr
                        .attr("transform", d => `translate(${d.x}, ${d.y})`);

                    nodeGroup.append("circle")
                        .attr("r", this.radius)
                        .attr("cx", 0)
                        .attr("cy", 0)
                        .attr("stroke", "blue")
                        .attr("fill", d => color(d.priority));

                    nodeGroup.append("text")
                        // .attr("x", 0)
                        // .attr("y", 0)
                        .attr("dy", 20)
                        .attr("stroke", "var(--text-muted)")
                        .attr("text-anchor", "middle")
                        .text(d => d.name);
                    
                    // Set up drag handlers
                    nodeGroup.call(d3.drag()
                        .on("start", function(event, d) {
                            // this._dragStarted
                            d3.select(this).select("circle")
                                .attr("fill", "red")
                                .style("cursor", "grabbing");

                        })
                        // .on("drag", this._dragged)
                        // .on("end", this._dragEnded)
                        .on("drag", function(event, d) {
                            d.x = Math.max(radius, Math.min(width - radius, event.x));
                            d.y = Math.max(radius, Math.min(height - radius, event.y));
                            d3.select(this).attr("transform", `translate(${d.x}, ${d.y})`);

                            // update links too?
                            capturedThis.updateLinks();
                        })
                        .on("end", function(event, d) {
                            d3.select(this).select("circle")
                                .attr("fill", d => color(d.priority))
                                .style("cursor", "grab")
                        })
                    )
                    .on('contextmenu', (event, d) => {
                        event.preventDefault();
                        const x = event.clientX;
                        const y = event.clientY;
                        console.log(`cursor x: ${x}, cursor y: ${y}`)
                        contextMenu.create({
                            position: { x: x, y: y },
                            items: [
                                {
                                    label: 'Delete',
                                    action: () => {
                                        // Filter out the el in nodes whose id === d.id
                                        this.nodes = this.nodes.filter(n => n.id !== d.id);
                                        // rebuilds this.nodes, nodesMap & updates links arr
                                        this.recomputeDerivedState();
                                        this.updateNodes();
                                        this.updateLinks();
                                    }
                                }
                            ]
                        })
                    })
                    .on('mouseenter', function(event, d) {
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
                        console.log(matches)
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
        this.linksContainer.selectAll("line")
            .data(this.links)
            .join(
                enter => {
                    const link = enter.append("line")
                        .attr("stroke", "#3f3f3f")
                        .attr("x1", d => {
                            const subtask = this.nodesMap.get(d.subtask)
                            return subtask.x;
                        })
                        .attr("y1", d => {
                            const subtask = this.nodesMap.get(d.subtask)
                            return subtask.y;
                        })
                        .attr("x2", d => {
                            const supertask = this.nodesMap.get(d.supertask)
                            return supertask.x;
                        })
                        .attr("y2", d => {
                            const supertask = this.nodesMap.get(d.supertask)
                            return supertask.y;
                        });
                    
                    link
                        .attr("stroke-linecap", "round")
                        .attr("marker-start", "url(#end)")

                    return link;
                },
                update => {
                    return update
                        .attr("x1", d => {
                            const subtask = this.nodesMap.get(d.subtask)
                            return subtask.x;
                        })
                        .attr("y1", d => {
                            const subtask = this.nodesMap.get(d.subtask)
                            return subtask.y;
                        })
                        .attr("x2", d => {
                            const supertask = this.nodesMap.get(d.supertask)
                            return supertask.x;
                        })
                        .attr("y2", d => {
                            const supertask = this.nodesMap.get(d.supertask)
                            return supertask.y;
                        });
                }
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
    const addBtn = document.querySelector('#add-node')!;
    addBtn.addEventListener('click', () => {
        thingies.addNode({
            id: 4, name: "Bobby"
        })
        thingies.addLink(1, 4)
        console.log(thingies.nodes)
    })
    // This mocks our DB join table for:
    // tasks_dependencies(task_id, prereq_id)
    const dummyLinks = [
        {subtask: 3, supertask: 2},
        {subtask: 6, supertask: 3}
    ]

    // grab some task info quick to see
    const url = routes.tasks.tasks.collection;
    console.log(url)
    const response = await apiRequest('GET', url, null);
    console.log(response.data)
    const pos = [
        200,
        200,
        200
    ]
    const posy = [
        400, // stretch
        200, // sdf
        600 // readme
    ]
    const tasksWithPositions: TaskNode[] = response.data.map((task: TaskNode, i: number) => ({
        ...task,
        x: pos[i] || 100 + (i * 100),
        y: posy[i] || 100 + (i * 100),
    }))
    console.log("response.data:")
    console.table(response.data)
    console.log(dummyLinks)

    const links = response.data.flatMap(task =>
        task.supertasks.map(supertaskId => ({
            subtask: task.id,
            supertask: supertaskId
        }))
    )
    console.log("Links:")
    console.log(links)

    const thingies = new CanvasManager(height, width, radius, tasksWithPositions, links);
    thingies.init();
    thingies.updateNodes();
    thingies.updateLinks();
    console.log(thingies.links)
    thingies.addLink(1, 2)
}

// drag event exposes:
// event.dx, event.dy : how much the mouse moved since last drag
// event.sourceEvent : original mouse/touch event if we need it
// event.x, event.y

// function dragStarted(event) {
//     d3.select(this)
//         .attr("fill", "red")
//     console.log("START")
// }

// function dragged(event) {
//     const d = d3.select(this).datum(); // gets the data bound to this element/node
//     console.table(d)

//     // Center must stay at least radius distance away from edges
//     // We need to re-set the node array's Pos values for this node
//     // BEFORE we then update visuals. Data > visual
//     d.x = Math.max(radius, Math.min(width - radius, event.x));
//     d.y = Math.max(radius, Math.min(height - radius, event.y));
//     debug.textContent = `${d.x.toFixed(2)} || ${d.y.toFixed(2)}`;

//     // not cx/cy but rather transform now that we need to move the GROUP, not the circle inside
//     d3.select(this)
//         .attr("transform", `translate(${d.x}, ${d.y})`)
//         // .attr("cx", d.x)
//         // .attr("cy", d.y);
// }

// function dragEnded(evet) {
//     d3.select(this)
//         .attr("fill", d => color(d))
//     console.log("ENDED")
// }
