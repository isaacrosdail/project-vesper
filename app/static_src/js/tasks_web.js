import * as d3 from 'd3';



const height = window.innerHeight;
const width = window.innerWidth;
const radius = 40;

const margin = { top: 20, right: 20, bottom: 30, left: 40 };
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

const debug = document.querySelector('#debug');
const color = d3.scaleOrdinal(d3.schemeCategory10);

const nodes = [
    {id: 1, x: 250, y: 390, name: "Plan project"},
    {id: 2, x: 360, y: 250, name: "Buy materials"},
    {id: 3, x: 145, y: 170, name: "Build thing"}
]
const links = [
    {source: 1, target: 2},
    {source: 1, target: 3},
    {source: 2, target: 3}
]
const pairs = nodes.map(node => [node.id, node]);
console.table(pairs)
const nodesMap = new Map(pairs);
console.log(nodesMap)

// Gist: draw a <line> from source <-> target, layered behind the nodes container
// So for that first link, we'd need to:
// 1. Get source's coords based on id
// 2. Get target's coords based on id
// 3. Draw a <line> from one to the other using said coords


class CanvasManager {
    constructor(height, width, radius) {
        this.height = height;
        this.width = width;
        this.radius = radius;
    }

    init() {
        // make SVG container
        this.svg = d3.select('#web')
            .append("svg")
            .attr("viewBox", [0, 0, this.width, this.height])
            .attr("style", "outline: 5px solid red")

        this.linksContainer = this.svg.append("g")
            .attr("class", "links")

        // make group for all nodes
        this.nodesContainer = this.svg.append("g")
            .attr("stroke", "cyan")
            .attr("stroke-width", 1.5)
            .style("outline", "1px solid red") // DEBUG

    }

    updateNodes(nodes) {
        // capture instance for updateLinks?
        const thingy = this;
        // initial graph of nodes setup?
        this.nodesContainer.selectAll("g.node") // g.node = a single node, in full (circle+text)
            .data(nodes, d => d.name)
            .join(
                enter => {
                    // Making a single node each time here in enter
                    const nodeGroup = enter.append("g")
                        .attr("class", "node")
                        .attr("transform", d => `translate(${d.x}, ${d.y})`);

                    nodeGroup.append("circle")
                        .attr("r", this.radius)
                        .attr("cx", 0)
                        .attr("cy", 0)
                        .attr("stroke", "blue")
                        .attr("fill", d => color(d));

                    nodeGroup.append("text")
                        .attr("x", 0)
                        .attr("y", 0)
                        .attr("stroke", "orange")
                        .attr("text-anchor", "middle")
                        .text(d => d.name);
                    
                    // Set up drag handlers
                    nodeGroup.call(d3.drag()
                        .on("start", function(event, d) {
                            // this._dragStarted
                            d3.select(this).select("circle").attr("fill", "red");
                        })
                        // .on("drag", this._dragged)
                        // .on("end", this._dragEnded)
                        .on("drag", function(event, d) {
                            d.x = Math.max(radius, Math.min(width - radius, event.x));
                            d.y = Math.max(radius, Math.min(height - radius, event.y));
                            d3.select(this).attr("transform", `translate(${d.x}, ${d.y})`);

                            // update links too?
                            thingy.updateLinks();
                        })
                        .on("end", function(event, d) {
                            d3.select(this).select("circle").attr("fill", d => color(d))
                        })
                    );
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

    updateLinks() {
        // create/update links between nodes
        this.linksContainer.selectAll("line")
            .data(links)
            .join(
                enter => {
                    const link = enter.append("line")
                        .attr("stroke", "cyan")
                        .attr("x1", d => {
                            const source = nodesMap.get(d.source)
                            return source.x;
                        })
                        .attr("y1", d => {
                            const source = nodesMap.get(d.source)
                            return source.y;
                        })
                        .attr("x2", d => {
                            const target = nodesMap.get(d.target)
                            return target.x;
                        })
                        .attr("y2", d => {
                            const target = nodesMap.get(d.target)
                            return target.y;
                        });

                    return link;
                },
                update => {
                    return update
                        .attr("x1", d => {
                            const source = nodesMap.get(d.source)
                            return source.x;
                        })
                        .attr("y1", d => {
                            const source = nodesMap.get(d.source)
                            return source.y;
                        })
                        .attr("x2", d => {
                            const target = nodesMap.get(d.target)
                            return target.x;
                        })
                        .attr("y2", d => {
                            const target = nodesMap.get(d.target)
                            return target.y;
                        });
                }
            )

    }

    addNode() {
        // do things
    }
}

export function init() {

    document.addEventListener('click', (e) => {
        console.log(`Clicked: ${e.target}`)
    })
    const addBtn = document.querySelector('#add-node');
    addBtn.addEventListener('click', (e) => {
        nodes.push({
            id: 1, x: 30, y: 30, name: "Bobby"
        })
        console.table(nodes)
    })
    const thingies = new CanvasManager(height, width, radius);
    thingies.init();
    thingies.updateNodes(nodes);
    thingies.updateLinks();
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
