import * as d3 from 'd3';

import { D3_TRANSITION_DURATION_MS, getChartDimensions } from './shared/charts';
import { api } from './shared/services/api';
import { createTooltip, removeTooltip } from './shared/ui/tooltip';
import { userState } from './shared/services/userState.svelte';
import type { DailyMetricsRead } from './apiTypes';


// NOTE: All target values are per day, can easily multiply up from there as needed
// for any given timeframe

// Current targets/weights for reference:
// Sleep     480m (8h) - 0.40
// Calories  3k        - 0.25
// Steps     10k       - 0.15
// Weight    82kg      - 0.20
//
// Then for time vs metrics subscore weighting:
// Metrics             - 0.55
// Exercise  ~0.7h     - 0.45

// Rest of time tracking for pillars:
// Career: 30h/week → ~4.3h/day
// Rest: 5h/week → ~0.7h/day
// Relationships: 7h/week → 1h/day

type HealthConfig = Record<keyof MetricsAggregates, MetricConfig>;

type MoreIsBetter = {
    target: number;
    weight: number;
    type: "more";
}

type CloserIsBetter = {
    target: number;
    weight: number;
    type: "closer";
    tolerance: number;
}

type MetricConfig = MoreIsBetter | CloserIsBetter;

type MetricsAggregates = Pick<
    DailyMetrics,
    "calories" | "steps" | "weight" | "sleep_duration_minutes"
>;

type PillarName = "Health" | "Career" | "Relationships" | "Rest" | "Purpose";
type PillarTimeTotals = Partial<Record<PillarName, number>>
type MetricDetail = { value: number; target: number; score: number; }


type RadarLayer = RadarDatum[];
type RadarDatum = {
    axis: PillarName;
    value: number;
    details?: PillarDetails;
}

// Use arr here to keep order predictable to match chartData
const PILLAR_ORDER = ["Health", "Rest", "Relationships", "Career", "Purpose"]

function scoreHealthMetrics(metricsValues: MetricsAggregates) {
    // Account for weight-adjustment for metrics with null values in the given range?
    // Config obj without vals:

    // const healthConfig: HealthConfig = {
    //     "sleep_duration_minutes": { target: 480, weight: 0.40, type: "closer", tolerance: 90 },
    //     "steps": { target: 10_000, weight: 0.15, type: "more" },
    //     "calories": { target: 2_700, weight: 0.25, type: "closer", tolerance: 600 },
    //     "weight": { target: 76, weight: 0.20, type: "closer", tolerance: 5 },
    // }
    // Get targets
    const healthConfig: HealthConfig = {
        "sleep_duration_minutes": { target: userState.me?.goals.sleep_duration_minutes || 480, weight: 0.40, type: "closer", tolerance: 90 },
        "steps": { target: userState.me?.goals.steps || 10_000, weight: 0.15, type: "more" },
        "calories": { target: userState.me?.goals.calories || 2_700, weight: 0.25, type: "closer", tolerance: 600 },
        "weight": { target: userState.me?.goals.weight || 76, weight: 0.20, type: "closer", tolerance: 5 },
    }

    // idk?
    const presentMetrics = Object.entries(healthConfig).filter(([key, _]) => metricsValues[key] !== null)
    const totalWeight = presentMetrics.reduce((sum, [_, cfg]) => sum + cfg.weight, 0)

    // So we get something like this for sleep from backend:
    // const metrics = { sleep: 410, steps: 2400, calories: 2400, weight: 82 } // ...etc
    let healthMetricsSubscore = 0;
    const healthDetails = {} // to store value/target/score inside details: { Health: {...} } directly
    for (const [key, config] of Object.entries(healthConfig)) {
        const value = metricsValues[key as keyof MetricsAggregates];
        if (value === null) continue;

        const score = config.type === 'closer'
            ? 1 - Math.min(Math.abs(value - config.target) / config.tolerance, 1)
            : Math.min(value / config.target, 1);

        healthMetricsSubscore += score * (config.weight / totalWeight);
        healthDetails[key] = { value, target: config.target, score };
    }

    return { healthMetricsSubscore, healthDetails }
}

function scoreTimePillars(timeValues: PillarTimeTotals) {
    const pillarScores: Record<string, number> = {}

    const targets = {
        "Career": 8,
        "Rest": 2,
        "Relationships": 2,
        "Health": 1
    };

    const timeDetails: Record<string, MetricDetail> = {}
    for (const pillar of Object.keys(targets)) {
        const totalMinutes = timeValues[pillar] ?? 0;
        const value = totalMinutes / 60;
        const score = Math.min((value) / targets[pillar], 1.0);
        pillarScores[pillar] = score;
        timeDetails[pillar] = { value, target: targets[pillar], score: score }
    }

    return { pillarScores, timeDetails }
}

function calcPillarScores(metricsValues: MetricsAggregates, timeValues: PillarTimeTotals) {

    // Health subscore combination?
    const { healthMetricsSubscore, healthDetails } = scoreHealthMetrics(metricsValues);
    const { pillarScores: timeScores, timeDetails } = scoreTimePillars(timeValues);

    // Health = 55% metrics + 45% exercise time
    const healthScore = healthMetricsSubscore * 0.55 + timeScores["Health"] * 0.45;
    healthDetails["exercise"] = timeDetails["Health"];

    const result = {
        scores: { ...timeScores, Health: healthScore },
        details: {
            Health: healthDetails,
            Career: timeDetails["Career"],
            Rest: timeDetails["Rest"],
            Relationships: timeDetails["Relationships"],
            Purpose: { value: 0.3, target: 0.3 } // TODO: un-hardcode
        }
    }
    return result
}

async function fetchPillarData() {
    // API call to get aggregate avgs
    const params = (days: number) => new URLSearchParams({ lastNDays: days.toString() })

    // Then for sparkline, we'll use 6 buckets over the 90d span?
    const params2 = new URLSearchParams({ lastNDays: String(90), numBuckets: String(6) })

    // Promise.all takes an arr of promises and waits for all of them in parallel?
    const [responseRecent, responseLongTerm, timeRecent, timeLongTerm, baselineBuckets] = await
    Promise.all([
        api.daily_metrics.aggregate(params(14)),
        api.daily_metrics.aggregate(params(90)),
        api.time_entries.aggregate(params(14)),
        api.time_entries.aggregate(params(90)),
        api.daily_metrics.aggregate(params2),
    ]);

    // Calculate pillar scores
    const { 
        scores: longScores,
        details: longDetails,
    } = calcPillarScores(responseLongTerm.data, timeLongTerm.data)
    longScores["Purpose"] = 0.3; // Placeholder

    const {
        scores: recentScores,
        details: recentDetails,
    } = calcPillarScores(responseRecent.data, timeRecent.data)
    recentScores["Purpose"] = 0.3; // Placeholder

    // Calc sparkline bucket scores:
    // Gives us an array of score objects, where arr[0] is the oldest
    const bucketScores = baselineBuckets.data.map(bucket => {
        if (!bucket) return null;
        const { scores } = calcPillarScores(bucket, timeLongTerm.data)
        return scores
    })

    // Then per pillar, pull its score across all buckets
    const sparklineData = PILLAR_ORDER.map(name => ({
        axis: name,
        history: bucketScores.map(b => b ? b[name] : null)
    }));
    // So sparklineData[0].history for Health would be: [0.72, 0.68, 0.61, 0.55, 0.48, 0.42]

    // Map to axis/value setup for radar chart
    const recentData = PILLAR_ORDER.map((name, i) => ({
        axis: name,
        value: recentScores[name],
        details: recentDetails[name],
        pctDiffVsBaseline: ((recentScores[name] - longScores[name]) / longScores[name]),
        history: sparklineData[i].history
    }))

    const baselineData = PILLAR_ORDER.map(name => ({
        axis: name,
        value: longScores[name],
        details: longDetails[name]
    }))

    // Consists, ultimately, of 3 arrs of objs:
    // 1. Maslow Minimums
    // 2. Long term scores (6-12mo rolling aggregate/avgs)
    // 3. Recent scores    (currently 14d, should make this interactible prob)
    const chartData = [
        [ // Maslow minimum thresholds
            { axis: "Health", value: 0.6 },
            { axis: "Rest", value: 0.5 },
            // "diversity index"? ie, hang out with more than 1-2 ppl
            { axis: "Relationships", value: 0.35 },
            { axis: "Career", value: 0.3 },
            { axis: "Purpose", value: 0.2 },
        ],
    ]
    chartData.push(baselineData)
    chartData.push(recentData)
    return chartData;
}

// Show tooltip with both vals
// What do we wanna show?
// 1. What's hurting us? -> lowest scoring sub-indicator: "Sleep: 6.2h (target: 8h)"
// 2. What's helping us? -> highest: "Steps: 11k (target: 10k)"
// 3. Trend: "^ 8% vs 90 avg"
// For the other pillars (Career, Rest, Relationships) it's simpler since they're just time-based:
// "Career: 72% — avg 4.3h/day (target: 6h)"
// "Rest: 31% — avg 0.6h/day (target: 2h)" ← oof
function tooltipText(d: RadarDatum): string {
    if (d.axis === "Health") {
        const lowest = Object.entries(d.details).reduce((acc, curr) => 
            acc[1].score < curr[1].score ? acc : curr
        )
        return `${d.axis}: ${Math.round(d.value * 100)}% - Weakest: ${lowest[0]} (${Math.round(lowest[1].score * 100)}%)`
    }
    return `${d.axis}: ${Math.round(d.value * 100)}% - ${d.details.value.toFixed(1)}h / ${d.details.target}h`
}

function renderRadarChart(radarLayers: RadarLayer[]) {

    // RADAR CHART STUFF
    const numAxes = PILLAR_ORDER.length;
    const angleSlice = (2 * Math.PI) / numAxes;
    const MAX_SCORE = 1;

    const dims = getChartDimensions('#radar-chart-container');
    const radius = dims.height / 2.5;

    // Helpers
    const polarX = (r: number, i: number) => r * Math.cos(i * angleSlice - Math.PI / 2);
    const polarY = (r: number, i: number) => r * Math.sin(i * angleSlice - Math.PI / 2);

    const svg = d3.select('#radar-chart-container').append("svg")
        .attr("width", dims.width)
        .attr("height", dims.height)

    // NOTE: Generator pattern: Configure it once (here), call it with
    // data via .datum() + .attr("d", radarLine)
    const radarLine = d3.lineRadial()
        .curve(d3.curveLinearClosed)
        .radius(d => rScale(d.value))
        .angle((_d, i) => i * angleSlice)

    // ???
    const sparkLine = d3.line<number>()
        .defined(v => v !== null) // ???
        .x((v, i, arr) => (i / (arr.length - 1)) * 80)
        .y(v => 30 - (v * 30));

    const rScale = d3.scaleLinear()
        .domain([0, MAX_SCORE])
        .range([0, radius])
    
    const gChart = svg.append("g")
        .attr("transform", `translate(${dims.width/2}, ${dims.height/2})`)

    const gLegend = svg.append("g")
        .attr("transform", `translate(0, ${dims.height -10})`)

    // gridlines
    const levels = 4;
    // for (let level = 1; level <= levels; level++) {
    //     const r = (radius / levels) * level;
    //     gChart.append("polygon")
            // .attr("points", radarLayers[0].map((_d, i) => {
            //     const angle = i * angleSlice - Math.PI / 2;
            //     return `${r * Math.cos(angle)},${r * Math.sin(angle)}`
            // }).join(" "))
    //         .attr("fill", "none")
    //         .attr("stroke", "var(--text-muted)")
    //         .attr("stroke-opacity", 0.3);
    // }

    gChart.selectAll(".grid-level")
        .data(d3.range(1, levels + 1))
        .join("polygon") // one polygon per lvl
        .attr("class", "grid-level")
        .attr("points", level => { // concat point strings with spaces
            const r = (radius / levels) * level;
            return radarLayers[0].map((_d, i) => {
                const angle = i * angleSlice - Math.PI / 2;
                return `${r * Math.cos(angle)},${r * Math.sin(angle)}`
            }).join(" ")
        })
        .attr("fill", "none")
        .attr("stroke", "var(--text-muted)")
        .attr("stroke-opacity", 0.3);

    // axis lines - spokes from center to pillar
    gChart.selectAll(".axis-line")
        .data(radarLayers[0])
        .join("line")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", (_d, i) => polarX(radius, i))     //radius * Math.cos(i * angleSlice - Math.PI / 2))
        .attr("y2", (_d, i) => polarY(radius, i))     // radius * Math.sin(i * angleSlice - Math.PI / 2))
        .attr("stroke", "var(--text-muted)")
        .attr("stroke-opacity", 0.3);

    // cos is positive -> label is right side
    // negative -> 
    const labelAngle = (i: number) => i * angleSlice - Math.PI / 2;
    const labelGroups = gChart.selectAll(".axis-label")
        .data(radarLayers[2])
        .join("text")
        .attr("x", (_d, i) => polarX(radius + 25, i))  // (radius + 25) * Math.cos(i * angleSlice - Math.PI / 2))
        .attr("y", (_d, i) => polarY(radius + 25, i))  // (radius + 25) * Math.sin(i * angleSlice - Math.PI / 2))
        .attr("text-anchor", (_d, i) => {
            const x = Math.cos(labelAngle(i));
            if (Math.abs(x) < 0.01) return "middle";
            return x > 0 ? "start" : "end";
        })
        .on('mouseenter', (_e, d) => {
            d3.select(`.axis-sparkline-${d.axis}`).attr("visibility", "visible")
        })
        .on('mouseleave', (_e, d) => {
            d3.select(`.axis-sparkline-${d.axis}`).attr("visibility", "hidden")
        })

    const PCT_THRESHOLD = 2
    const trendArrow = pct => pct > PCT_THRESHOLD ? '↑' : pct < -PCT_THRESHOLD ? '↓' : '→';
    const trendColor = pct => pct > PCT_THRESHOLD ? '#22c55e' : pct < -PCT_THRESHOLD ? '#f87171' : '#f59e0b';
    labelGroups.append("tspan")
        .text(d => d.axis)
        .attr("fill", "#94a3b8")

    labelGroups.append("tspan")
        .attr("dx", 6)
        .text(d => trendArrow(d.pctDiffVsBaseline))
        .attr("fill", d => trendColor(d.pctDiffVsBaseline))


    const sparkGroups = gChart.selectAll(".axis-sparkline")
        .data(radarLayers[2])
        .join("g")
        .attr("class", d => `axis-sparkline-${d.axis}`)
        .attr("transform", (_d, i) => {
            const label = labelGroups.nodes()[i]; // nodes() gives us raw DOM els arr - [i] for 'this one' ofc
            const bbox = label.getBBox(); // actual rendered text for labels to align box pinned bottom-left
            // const x = (radius + 25) * Math.cos(i * angleSlice - Math.PI / 2);
            // const y = (radius + 25) * Math.sin(i * angleSlice - Math.PI / 2);
            // return `translate(${x}, ${y})`
            return `translate(${bbox.x}, ${bbox.y + bbox.height + 5})`
        })
        .attr("visibility", "hidden")
        .attr("fill", "red")

    sparkGroups.append("rect")
        .attr("width", 120)
        .attr("height", 50)
        .attr("fill", "var(--bg-light)")
        .attr("rx", 4)

    sparkGroups.append("text")
        .attr("dy", 15)
        .attr("dx", 60)
        .text(d => {
            const diffSign = d.pctDiffVsBaseline > 0 ? '+' : '';
            return `${diffSign}${d.pctDiffVsBaseline.toFixed(2)}%`
        })

    // Try hardcoding
    const points = [[0, 30], [20,20], [40,25], [60,10], [80,15]]
    sparkGroups.append("polyline")
        // .attr("points", points.map(([x,y]) => `${x},${y}`).join(' '))
        // .attr("points", d => d.history
        //     .filter(v => v !== null)
        //     .map((v, i, arr) => {
        //         const x = (i / (arr.length - 1)) * 80
        //         const y = 30 - (v * 30)
        //         return `${x},${y}`
        //     })
        //     .join(' ')
        // )
        .attr("d", d => sparkLine(d.history)) // TODO: Same as polyline? not working either lmao
        .attr("fill", "none")
        .attr("stroke", "#94a3b8")
        .attr("stroke-width", 1.5)
        .attr("stroke-linecap", "round")
        .attr("stroke-linejoin", "round")

    // Red = Maslow minimum, Yellow = trend?, Blue = current.
    const color = d3.scaleOrdinal()
        .range(["#CC333F","#6eb2ba","var(--accent-subtle)"])
    // #00A0B0

    const legendItems = [
        {label: "Minimum", color: "var(--radar-minimum)", style: "dashed"},
        {label: "Baseline", color: "var(--radar-baseline)"},
        {label: "Recent", color: "var(--accent-subtle)"}
    ]

    const item = gLegend.selectAll("g")
        .data(legendItems)
        .enter()
        .append("g")
        .attr("transform", (d, i) => `translate(${i * 120}, 0)`)

    item.append("line")
        .attr("x1", 0).attr("x2", 20)
        .attr("y1", 0).attr("y2", 0)
        .attr("stroke", d => d.color)
        .attr("stroke-width", 3)
        .attr("stroke-dasharray", d => {
            if (d.style === "dashed") return "2,4";
            return null;
        });

    item.append("text")
        .attr("x", 26)
        .attr("y", 5)
        .text(d => d.label)

    const layerStyles = [
        { dash: "6 4", fill: "none", fillOpacity: 0, stroke: "var(--radar-minimum)", strokeWidth: 1.5, opacity: 0.7 },
        { dash: null, fill: "var(--radar-baseline)", fillOpacity: 0.12, stroke: "var(--radar-baseline)", strokeWidth: 1.5, opacity: 1 },
        { dash: null, fill: "var(--accent-subtle)", fillOpacity: 0.15, stroke: "var(--accent-subtle)", strokeWidth: 2.5, opacity: 1 },
    ];

    gChart.selectAll(".radar-layer")
        .data(radarLayers.map((layer, i) => ({ points: layer, style: layerStyles[i] })))
        .join("path")
        .attr("class", "radar-layer")
        .attr("d", d => radarLine(d.points))
        .attr("fill", d => d.style.fill)
        .attr("fill-opacity", d => d.style.fillOpacity)
        .attr("stroke", d => d.style.stroke)
        .attr("stroke-width", d => d.style.strokeWidth)
        .attr("stroke-dasharray", d => d.style.dash)
        .attr("opacity", d => d.style.opacity)

    // trying stuff out
    const DOT_INITIAL_RADIUS = 4;
    gChart.selectAll(".vertex-dot")
        .data(radarLayers[2])
        .join("circle")
        .attr("cx", (d, i) => rScale(d.value) * Math.cos(i * angleSlice - Math.PI / 2))
        .attr("cy", (d, i) => rScale(d.value) * Math.sin(i * angleSlice - Math.PI / 2))
        .attr("r", DOT_INITIAL_RADIUS)
        .attr("fill", "none")
        .attr("stroke", "var(--accent-strong)")
        .on("mouseenter", (event, d) => {
            // Add fill
            d3.select(event.currentTarget)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("fill", "var(--accent-strong)")
                .attr("r", 6);

            const longVal = radarLayers[1].find(l => l.axis === d.axis)?.value ?? 0;
            // const shortVal = radarLayers[2].find(s => s.axis === d.axis)?.value ?? 0;
            createTooltip(event.currentTarget, tooltipText(d))
        })
        .on('mouseleave', (event) => {
            d3.select(event.currentTarget)
                .transition().duration(D3_TRANSITION_DURATION_MS)
                .attr("fill", "none")
                .attr("r", DOT_INITIAL_RADIUS);
            removeTooltip(event.currentTarget)
        })
}


export async function init() {
    const radarLayers = await fetchPillarData();
    renderRadarChart(radarLayers);

    const radarContainer = document.querySelector('.radar-container');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            e.target.classList.toggle("visible", e.isIntersecting);
        });
    }, {
        threshold: 0.5
    })
    observer.observe(radarContainer);
    
    // DRAFT: For the 3d stuff
    const draftContainer = document.querySelector<HTMLElement>('.draft-container');
    const thing = draftContainer.getBoundingClientRect();
    const [centerX, centerY] = [thing.width / 2, thing.height / 2]
    const DEFAULT_X = '60deg';
    const DEFAULT_Y = '0deg';
    const deadzone = 30;
    draftContainer.addEventListener('mousemove', (e: MouseEvent) => {
        if (e.offsetX < deadzone || e.offsetX > thing.width - deadzone ||
            e.offsetY < deadzone || e.offsetY > thing.height - deadzone) {
            return;
        }
        const normalizedX = (e.offsetX - centerX) / centerX
        const normalizedY = (e.offsetY - centerY) / centerY
        const rotateX = 60 + normalizedX * 10;
        const rotateY = normalizedY * 10;
        draftContainer.style.transition = 'none';
        draftContainer.style.setProperty('--rotate-x-amt', `${rotateX}deg`)
        draftContainer.style.setProperty('--rotate-y-amt', `${rotateY}deg`)
    })
    draftContainer.addEventListener('mouseleave', (e: MouseEvent) => {
        draftContainer.style.transition = 'transform 0.7s ease';
        draftContainer.style.setProperty('--rotate-x-amt', `${DEFAULT_X}`)
        draftContainer.style.setProperty('--rotate-y-amt', `${DEFAULT_Y}`)
    })
}