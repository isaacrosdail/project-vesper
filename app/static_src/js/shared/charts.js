import * as d3 from 'd3';
// Getting started with D3.js
// chart-container id in style-reference page

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

// Grab weather data here too for learning
// const response = await fetch(`/api/weather/London/metric`)
// const weatherData = await response.json()

// const tempMin = weatherData.main.temp_min;
// const tempMax = weatherData.main.temp_max;

// console.log('Got temps: ', tempMin, tempMax);

// Create the svg
const svg = d3.select('#chart-container')
    .append("svg")
    .attr("width", 500)
    .attr("height", 300);

function drawChart (data) {    // Apply attributes & fill chart with rect's
    const rects =  d3.select("svg")
        .selectAll("rect") // pre-emptively select the rects we're making
        .data(data)     // pass data into chart?

    // Enter / Update / Exit pattern

    // Enter => Handle NEW data
    const enterRects = rects.enter()           // "enter the rect-making part" kinda?
        .append("rect")    // append rect elements inside our svg graph?
        .attr("x", (d, i) => i * 50)     // set a fixed x-width
        .attr("y", 300)    // start all bars at bottom
        .attr("width", 40)
        .attr("height", 0) // start with zero height
        .attr("fill", "var(--accent-subtle)")

    // Update => Handle EXISTING data - merge enter + existing
    enterRects.merge(rects)
        .transition()
        .duration(1000)
        .attr("y", d => 300 - d) // Start the bar THIS far down from the bottom
                                // This (containerHeight - dataValue) math pattern is super common in D3, we'll see it everywhere for bottom-up charts
        .attr("height", d => d)  // bar extends DOWN from that y position
}

// drawChart([tempMin, tempMax]);
drawChart([50, 40, 42, 20, 15]);
// setTimeout(() => {
//     drawChart([50, 40, 42, 20, 15]);
// }, 7000);