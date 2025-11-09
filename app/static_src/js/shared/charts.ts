import * as d3 from 'd3';
// Getting started with D3.js
// chart-container id in style-reference page

type BarValue = number;

type LineDatum = {
    time: string;
    temp: number;
}

type BarDatum = {
    category: string;
    value: number;
}

// const data = [10, 20, 30, 40];
// const data = [5, 15, 25, 35, 45];
// const svg = d3.select('#chart-container')
//     .append("svg")
//     .attr("width", 500)
//     .attr("height", 300);

// d3.select("svg")
//   .selectAll("circle") // Note at this point we have no circles! We're saying "I want to select all the circles that SHOULD exist for my data"
//   .data(data)
//   .enter()             // ..."oh there aren't yet any circles? That's what .enter is for!"
//   .append("rect")
//   // data join: D3 automatically creates new elements for new data, adding another data value auto-makes another circle :D
//   .attr("x", (d, i) => i * 50 + 25)  // x position
//   .attr("y", 50)                     // y position  
//   .attr("width", d => d)             // width from data

const width = 500;
const height = 500;

// Create the svg
const barSvg = d3.select('#chart-container')
    .append("svg")
    .attr("width", width)
    .attr("height", height);

function drawChart (data: BarValue[]) {    // Apply attributes & fill chart with rect's
    const rects =  barSvg.selectAll<SVGRectElement, BarValue>("rect")
        .data(data)     // pass data into chart?
        .join(
            enter => enter
                .append("rect")    // append rect elements inside our svg graph?
                .attr("x", (_d, i) => i * 50)     // set a fixed x-width
                .attr("y", 300)    // start all bars at bottom
                .attr("width", 40)
                .attr("height", 0) // start with zero height
                .attr("fill", "var(--accent-subtle)"),
            update => update
                .transition()
                .duration(1000)
                .attr("y", d => 300 - d) // Start the bar THIS far down from the bottom
                                        // This (containerHeight - dataValue) math pattern is super common in D3, we'll see it everywhere for bottom-up charts
                .attr("height", d => d),  // bar extends DOWN from that y position
            exit => exit.remove()
        )
}

drawChart([50, 40, 42, 20, 15]);


function renderLineChart(height: number, width: number, lineData: LineDatum[]) {
    const svgLine = d3.select('#time-chart')
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g");

    // evenly spacing labels (strings) across a range -> scalePoint
    // OR use scaleTime(), requiring real Date objects
    const xScaleLine = d3.scalePoint()
        .domain(lineData.map(d => d.time))
        .range([0, width])
        .padding(0.5);

    // temps are numeric -> scaleLinear
    const yScaleLine = d3.scaleLinear()
        .domain([55, 80])
        .range([height, 0]);

    // Line generator
    const line = d3.line<LineDatum>()
        .x(d => xScaleLine(d.time)!)
        .y(d => yScaleLine(d.temp));

    svgLine.append("path")
        .datum(lineData)
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", "var(--accent-strong)")
        .attr("stroke-width", 2);
}


function renderBarGraph(
    height: number,
    width: number,
    data: BarDatum[]
): void {
    // Bar chart
    const svg2 = d3.select('#time-chart')
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g") // <g> -> SVG group element. Container that lets you group other SVG elements (<rect>, <text>, etc)

    // scaleBand() is for categorical spacing (x-axis, bars)
    const xScale = d3.scaleBand<string>()
        .domain(data.map(d => d.category)) // ["Programming", "Meetings", "Break"]
        .range([0, width])                 // From 0px to 300px
        // .range([50, width-50]) // Changing x.range() just changes _where_ in the SVG the data is drawn, NOT the SVG (width) itself. Therefore this would just leave gaps on either side
        .padding(0.2);                     // 10% gap between bars

    // scaleLinear() is for numeric (y-axis, bars)
    const yMax = d3.max(data, d => d.value) ?? 0;
    const yScale = d3.scaleLinear()
        .domain([0, yMax]) // makes the "y-cap" of chart equal the largest y-val in dataset
        // .domain([0, 100]) // this would just make the max y-val of chart be 100, regardless of whether that fits our data our not
        .range([height, 0]);

    svg2.selectAll("rect") // grab placeholders for our bars (dont exist yet)
        .data(data) // bind dataset to data
        .enter() // enter the datajoin phase (create new DOM for each datum)
        .append("rect") // actually create a <rect>
        .attr("class", "bar")
        .attr("x", d => xScale(d.category)!)  // x-position of bar
        .attr("y", d => yScale(d.value))     // y-position of top of bar
        .attr("width", xScale.bandwidth())   // width of bar using bandwidth() found earlier in the 'const x = ...' part
        .attr("height", d => height - yScale(d.value))  // height of bar (y inverted cause graphics)
        .attr("fill", "var(--accent-strong)");
}