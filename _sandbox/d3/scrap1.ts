import * as d3 from 'd3';

type BarValue = number;

type LineDatum = {
    time: string;
    temp: number;
}

type BarDatum = {
    category: string;
    value: number;
}

export interface ChartDimensions {
    width: number;
    height: number;
    innerWidth: number;
    innerHeight: number;
    margin: { top: number; right: number; bottom: number; left: number; }
}

export const D3_TRANSITION_DURATION_MS = 200;

/**
 * Helper to get/set up chart dimensions for D3 charts.
 * @param containerSelector 
 * @param margin 
 */
export function getChartDimensions(
    containerSelector: string,
    margin = { top: 20, right: 20, bottom: 30, left: 40 }
): ChartDimensions {
    const container = document.querySelector(containerSelector) as HTMLElement;

    const width = container.clientWidth || 400;
    const height = container.clientHeight || 400;

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    return { width, height, innerWidth, innerHeight, margin };
}


// const width = 500;
// const height = 500;

// // Create the svg
// const barSvg = d3.select('#asdfasdf')
//     .append("svg")
//     .attr("width", width)
//     .attr("height", height);

// function drawChart (data: BarValue[]) {    // Apply attributes & fill chart with rect's
//     const _rects =  barSvg.selectAll<SVGRectElement, BarValue>("rect")
//         .data(data)     // pass data into chart?
//         .join(
//             enter => enter
//                 .append("rect")    // append rect elements inside our svg graph?
//                 .attr("x", (_d, i) => i * 50)     // set a fixed x-width
//                 .attr("y", 300)    // start all bars at bottom
//                 .attr("width", 40)
//                 .attr("height", 0) // start with zero height
//                 .attr("fill", "var(--accent-subtle)"),
//             update => update
//                 .transition()
//                 .duration(1000)
//                 .attr("y", d => 300 - d) // Start the bar THIS far down from the bottom
//                                         // This (containerHeight - dataValue) math pattern is super common in D3, we'll see it everywhere for bottom-up charts
//                 .attr("height", d => d),  // bar extends DOWN from that y position
//             exit => exit.remove()
//         )
// }

// drawChart([50, 40, 42, 20, 15]);


// function _renderLineChart(height: number, width: number, lineData: LineDatum[]) {
//     const svgLine = d3.select('#chart-container')
//         .append("svg")
//         .attr("width", width)
//         .attr("height", height)
//         .append("g");

//     // evenly spacing labels (strings) across a range -> scalePoint
//     // OR use scaleTime(), requiring real Date objects
//     const xScaleLine = d3.scalePoint()
//         .domain(lineData.map(d => d.time))
//         .range([0, width])
//         .padding(0.5);

//     // temps are numeric -> scaleLinear
//     const yScaleLine = d3.scaleLinear()
//         .domain([55, 80])
//         .range([height, 0]);

//     // Line generator
//     const line = d3.line<LineDatum>()
//         .x(d => xScaleLine(d.time)!)
//         .y(d => yScaleLine(d.temp));

//     svgLine.append("path")
//         .datum(lineData)
//         .attr("d", line)
//         .attr("fill", "none")
//         .attr("stroke", "var(--accent-strong)")
//         .attr("stroke-width", 2);
// }


// function _renderBarGraph(
//     height: number,
//     width: number,
//     data: BarDatum[]
// ): void {
//     // Bar chart
//     const svg2 = d3.select('#chart-container')
//         .append("svg")
//         .attr("width", width)
//         .attr("height", height)
//         .append("g") // <g> -> SVG group element. Container that lets you group other SVG elements (<rect>, <text>, etc)

//     // scaleBand() is for categorical spacing (x-axis, bars)
//     const xScale = d3.scaleBand<string>()
//         .domain(data.map(d => d.category)) // ["Programming", "Meetings", "Break"]
//         .range([0, width])                 // From 0px to 300px
//         // .range([50, width-50]) // Changing x.range() just changes _where_ in the SVG the data is drawn, NOT the SVG (width) itself. Therefore this would just leave gaps on either side
//         .padding(0.2);                     // 10% gap between bars

//     // scaleLinear() is for numeric (y-axis, bars)
//     const yMax = d3.max(data, d => d.value) ?? 0;
//     const yScale = d3.scaleLinear()
//         .domain([0, yMax]) // makes the "y-cap" of chart equal the largest y-val in dataset
//         // .domain([0, 100]) // this would just make the max y-val of chart be 100, regardless of whether that fits our data our not
//         .range([height, 0]);

//     svg2.selectAll("rect") // grab placeholders for our bars (dont exist yet)
//         .data(data) // bind dataset to data
//         .enter() // enter the datajoin phase (create new DOM for each datum)
//         .append("rect") // actually create a <rect>
//         .attr("class", "bar")
//         .attr("x", d => xScale(d.category)!)  // x-position of bar
//         .attr("y", d => yScale(d.value))     // y-position of top of bar
//         .attr("width", xScale.bandwidth())   // width of bar using bandwidth() found earlier in the 'const x = ...' part
//         .attr("height", d => height - yScale(d.value))  // height of bar (y inverted cause graphics)
//         .attr("fill", "var(--accent-strong)");
// }