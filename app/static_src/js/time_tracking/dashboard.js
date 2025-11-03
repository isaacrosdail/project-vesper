import * as d3 from 'd3';

import { hideToolTip, showToolTip } from '../shared/ui/tooltip';
import { apiRequest } from '../shared/services/api';

// Set up dimensions
const width = 300;
const height = 300;
const radius = Math.min(width, height) / 2;

// Pie chart
const svg = d3.select('#time-chart')
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width/2}, ${height/2})`);

// d3.pie() takes our array data and calculates angles
const pie = d3.pie().value(d => d.value);
// d3.arc() draws the curved slice shapes based on those angles
const arc = d3.arc().innerRadius(0).outerRadius(radius);
// Color Scale maps indexes to colors
const color = d3.scaleOrdinal(d3.schemeCategory10);


function updatePieChart(data) {
    let disableHoverEffects = data.length === 0 || data.length === 1;

    if (data.length === 0) {
        data = [{ category: 'No data', value: 1}];
    }
    const pieData = pie(data);

    const groups = svg.selectAll("g.slice")
        // .data(data, keyFn)
        .data(pieData, d => d.data.category) // key function = stable matching?
        .join(
            enter => {
                const g = enter.append("g").attr("class", "slice");

                // path (slice)
                g.append('path')
                    .attr("class", "pie tooltip")
                    .attr("fill", d => color(d.data.category))
                    .each(function(d) { this._current = d; }) // store start?
                    .attr("d", arc);

                g.append("text")
                    .attr("text-anchor", "middle")
                    .attr("alignment-baseline", "middle")
                    .text(d => `${d.data.category} (${d.data.value})`)
                    .attr("transform", d => `translate(${arc.centroid(d)})`);

                return g;
            },
            update => {
                // update paths
                update.select("path")
                    .transition().duration(500)
                    .attrTween("d", function(d) {
                        const i = d3.interpolate(this._current, d);
                        this._current = i(1);
                        return t => arc(i(t));
                    });

                // update labels
                update.select("text")
                    .transition().duration(500)
                    .text(d => `${d.data.category} (${d.data.value})`)
                    .attr("transform", d => `translate(${arc.centroid(d)})`);

                return update;
            },
            exit => exit.remove()
        );

    const legend = svg.selectAll("g.legend")
        .data(pieData, d => d.data.category)
        .join(
            enter => {
                const g = enter.append("g").attr("class", "legend");

                // Position each below the last
                g.attr("transform", (d, i) => {
                    return `translate(170, ${-130 + (i * 22)})`
                })
                // legend circle
                g.append('circle')
                    .attr("cx", 10)
                    .attr("cy", 10)
                    .attr("r", 6)
                    .attr("class", "pie legend-dot")
                    .attr("fill", d => color(d.data.category));

                // text alongside
                g.append('text')
                    .attr("x", 18)
                    .attr("y", 14)
                    .text(d => `${d.data.category} - ${d.data.value} min`)

                return g;
            },
            update => {
                // Update transform to update positions
                update.attr("transform", (d, i) => {
                    return `translate(200, ${i * 20})`
                })
                return update;
            },
            exit => exit.remove()
        )

    // Enable tooltip on hover to see data
    groups.on('mouseenter', function(event, d) {
        if (disableHoverEffects) return;

        showToolTip(this, `${d.data.category}: ${d.data.value}`);

        // Calc midpoint (angle)
        const rawMidpoint = (d.startAngle + d.endAngle) / 2;
        const midpoint = rawMidpoint - (Math.PI / 2);
        const dist = radius / 10;
        console.log(midpoint);

        // Calc x, y for transform
        const x = Math.cos(midpoint) * dist;
        const y = Math.sin(midpoint) * dist;

        // Transform
        d3.select(this)
            .transition().duration(200)
            .attr("transform", `translate(${x}, ${y})`);
    });
    groups.on('mouseleave', function(event, d) {
        if (disableHoverEffects) return;

        hideToolTip();

        d3.select(this)
            .transition().duration(200)
            .attr("transform", "translate(0, 0)");
    });
}

function renderBarGraph(height, width, data) {
    // Bar chart
    const svg2 = d3.select('#time-chart')
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g") // <g> -> SVG group element. Container that lets you group other SVG elements (<rect>, <text>, etc)

    // scaleBand() is for categorical spacing (x-axis, bars)
    const x = d3.scaleBand()
        .domain(data.map(d => d.category)) // ["Programming", "Meetings", "Break"]
        .range([0, width])                 // From 0px to 300px
        // .range([50, width-50]) // Changing x.range() just changes _where_ in the SVG the data is drawn, NOT the SVG (width) itself. Therefore this would just leave gaps on either side
        .padding(0.2);                     // 10% gap between bars

    // scaleLinear() is for numeric (y-axis, bars)
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)]) // makes the "y-cap" of chart equal the largest y-val in dataset
        // .domain([0, 100]) // this would just make the max y-val of chart be 100, regardless of whether that fits our data our not
        .range([height, 0]);

    svg2.selectAll("rect") // grab placeholders for our bars (dont exist yet)
        .data(data) // bind dataset to data
        .enter() // enter the datajoin phase (create new DOM for each datum)
        .append("rect") // actually create a <rect>
        .attr("class", "bar")
        .attr("x", d => x(d.category))  // x-position of bar
        .attr("y", d => y(d.value))     // y-position of top of bar
        .attr("width", x.bandwidth())   // width of bar using bandwidth() found earlier in the 'const x = ...' part
        .attr("height", d => height - y(d.value))  // height of bar (y inverted cause graphics)
        .attr("fill", "var(--accent-strong)");
}

function renderLineChart(height, width, lineData) {
    // Line chart
    const svgLine = d3.select('#time-chart')
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")

    // Times here are discrete labels, not numeric time values. We can use scalePoint() for this: evenly spacing labels (strings) across a range
    // NOTE: Upgrade to scaleTime() (requires real Date objects)
    const xScale = d3.scalePoint()
        .domain(lineData.map(d => d.time))
        .range([0, width])
        .padding(0.5);

    // Since temps here are numeric in nature, we use scaleLinear()
    const yScale = d3.scaleLinear()
        .domain([55, 80])
        .range([height, 0]);

    // For line charts, we'll need to use D3's lineGenerator using .line() first as an intermediary step before drawing
    const lineGenerator = d3.line()
        .x(d => xScale(d.time))
        .y(d => yScale(d.temp));

    // Then we draw the line using the path element
    svgLine.append("path")
        .datum(lineData) // notice we use .datum(lineData) not .data(lineData) because we're passing the whole array, not mapping one path per data point
        .attr("d", lineGenerator) // generates the line path
        .attr("fill", "none")
        .attr("stroke", "var(--accent-strong)")
        .attr("stroke-width", 2);
}

export async function init() {
    // Render initial pie chart
    const data = await getData(7);
    updatePieChart(data);


    document.addEventListener('click', async (e) => {
        if (e.target.matches('.timeframe-selection')) {
            console.log("test")
            const range = parseInt(e.target.dataset.range, 10);
            const data = await getData(range);
            updatePieChart(data);
        }
    });
}

function getData(lastNDays) {
    return new Promise((resolve, reject) => {
        const url = `/time_tracking/time_entries/summary/pie?lastNDays=${lastNDays}`;
        apiRequest('GET', url, (responseData) => {
            const entries = responseData.data;
            
            if(Array.isArray(entries) && entries.length === 0) {
                return resolve([]);
            }
            // const rollup = d3.rollup(data, reducerFn, keyFn);
            const rollupMap = d3.rollup(
                entries,
                v => d3.sum(v, d => d.duration_minutes),
                d => d.category
            );
            const arr = [...rollupMap].map(([k, v]) => ({category: k, value: v}));
            console.log(arr);
            resolve(arr);
        }, reject);
    });
}