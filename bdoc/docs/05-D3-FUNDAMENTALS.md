# Chapter 05: D3 Fundamentals — Your First Bar Chart

## What you'll learn

- What SVG is and why D3 uses it
- How D3 selections work (select, selectAll, data binding)
- How to create a bar chart from an array
- How scales translate data values to pixel positions

## 5.1 What is SVG?

SVG (Scalable Vector Graphics) is like HTML but for graphics. Instead of `<div>` and `<p>`, you have `<rect>`, `<circle>`, `<line>`, `<text>`.

```html
<svg width="200" height="100">
  <rect x="10" y="10" width="50" height="80" fill="blue" />
  <circle cx="100" cy="50" r="30" fill="red" />
</svg>
```

This draws a blue rectangle and a red circle. Every shape is an element in the DOM — you can inspect it, style it with CSS, animate it.

> **Why SVG instead of Canvas?** SVG elements are DOM nodes — D3 can select them, transition them, attach events to them. Canvas is a pixel buffer — once you draw something, it's gone. You'd have to redraw everything on every frame. SVG is slower for thousands of elements but perfect for our use case (usually < 100 elements).
>
> **Canvas alternative:** For visualising very large datasets (10,000+ data points), Canvas or WebGL is better. For algorithm visualisation with 10-50 elements, SVG is ideal.

## 5.2 How D3 thinks

D3 doesn't draw charts for you. It's a toolkit for binding data to DOM elements. The mental model:

```
DATA  →  D3  →  DOM ELEMENTS
[5, 3, 8, 2]    [rect, rect, rect, rect]
```

Each number in your array becomes one visual element. D3's job is to create, update, and remove elements to match your data.

This is fundamentally different from Chart.js (which gives you `new BarChart(data)` and handles everything). D3 gives you building blocks — more work, but total control.

## 5.3 Create a BarChart component

Create `app/algorithms/components/BarChart.tsx`:

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

type BarChartProps = {
  data: number[];
  highlightIndices?: number[];
  width?: number;
  height?: number;
};

export default function BarChart({
  data,
  highlightIndices = [],
  width = 500,
  height = 300,
}: BarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous render

    const margin = { top: 20, right: 20, bottom: 30, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const xScale = d3
      .scaleBand()
      .domain(data.map((_, i) => String(i)))
      .range([0, innerWidth])
      .padding(0.2);

    const yScale = d3
      .scaleLinear()
      .domain([0, d3.max(data) || 0])
      .range([innerHeight, 0]);

    // Bars
    g.selectAll("rect")
      .data(data)
      .enter()
      .append("rect")
      .attr("x", (_, i) => xScale(String(i)) || 0)
      .attr("y", (d) => yScale(d))
      .attr("width", xScale.bandwidth())
      .attr("height", (d) => innerHeight - yScale(d))
      .attr("fill", (_, i) =>
        highlightIndices.includes(i) ? "#f59e0b" : "#3b82f6"
      )
      .attr("rx", 4); // rounded corners

    // Value labels on top of bars
    g.selectAll("text")
      .data(data)
      .enter()
      .append("text")
      .attr("x", (_, i) => (xScale(String(i)) || 0) + xScale.bandwidth() / 2)
      .attr("y", (d) => yScale(d) - 5)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#374151")
      .text((d) => d);
  }, [data, highlightIndices, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}
```

**This is dense. Let's break it down piece by piece.**

## 5.4 Understanding `useRef` and the SVG reference

```tsx
const svgRef = useRef<SVGSVGElement>(null);
// ...
return <svg ref={svgRef} ... />;
```

`useRef` gives you a reference to an actual DOM element. Think of it as `document.getElementById("my-svg")` but type-safe and tied to the component lifecycle.

D3 needs a DOM element to work with. We create the `<svg>` in JSX, then give D3 access to it via the ref.

> **Why not let React render the SVG elements?** You could: `{data.map(d => <rect ... />)}`. This is called "React-controlled SVG" and it works for simple cases. We use D3 directly because:
> 1. D3's transition API is much more powerful than CSS transitions for SVG
> 2. D3's data binding handles enter/update/exit patterns cleanly
> 3. Most D3 examples and documentation use direct DOM manipulation — easier to follow along
>
> **Alternative: React + D3 hybrid.** Use React for layout and D3 only for calculations (scales, axes). Many production apps do this. We'll show this pattern in Chapter 12.

## 5.5 Understanding scales

This is the most important D3 concept. A scale is a function that maps data values to visual values:

```
Data domain:  [0, 1, 2, 3, 4]  →  xScale  →  Pixel range: [0px, 100px, 200px, 300px, 400px]
Data domain:  [0 ... 50]        →  yScale  →  Pixel range: [300px ... 0px]  (inverted!)
```

### scaleBand (for x-axis — categorical)

```tsx
const xScale = d3
  .scaleBand()
  .domain(data.map((_, i) => String(i)))  // categories: "0", "1", "2", ...
  .range([0, innerWidth])                   // spread across the width
  .padding(0.2);                            // 20% gap between bars
```

`scaleBand` divides a range into equal bands. Perfect for bar charts where each bar has equal width.

`xScale("2")` returns the x-position for the 3rd bar. `xScale.bandwidth()` returns the width of each bar.

### scaleLinear (for y-axis — numerical)

```tsx
const yScale = d3
  .scaleLinear()
  .domain([0, d3.max(data) || 0])  // data range: 0 to maximum value
  .range([innerHeight, 0]);         // pixel range: bottom to top (inverted!)
```

**Why is the range inverted?** In SVG, y=0 is the TOP. Larger y values go DOWN. But in a bar chart, larger values should go UP. By inverting the range (`[bottom, top]`), a data value of 0 maps to the bottom, and the maximum maps to the top.

```
Data: 50  →  yScale(50)  →  0px   (top of chart)
Data: 25  →  yScale(25)  →  150px (middle)
Data: 0   →  yScale(0)   →  300px (bottom)
```

> **Why not just do `height - y` manually?** You could! Scales are just convenience functions. But they handle edge cases (clamping, nice tick values) and make your code declarative: "map THIS range to THAT range" rather than doing arithmetic everywhere.

## 5.6 Understanding data binding

```tsx
g.selectAll("rect")    // Select all existing rects (initially: none)
  .data(data)          // Bind data array to the selection
  .enter()             // For each datum without a matching element...
  .append("rect")      // ...create a new rect
  .attr("x", ...)      // ...set its attributes based on the datum
```

This is D3's core pattern: **select → data → enter → append**.

Think of it as a SQL JOIN between your data and the DOM:

| Data item | DOM element | Action |
|-----------|-------------|--------|
| Has data, no element | — | **Enter**: create element |
| Has data AND element | — | **Update**: modify element |
| No data, has element | — | **Exit**: remove element |

For our first render, all items enter (nothing exists yet). Later, when data changes, some update and some exit.

## 5.7 Wire the BarChart into the page

Update `app/algorithms/page.tsx` — add inside the VisualisationPanel:

```tsx
import BarChart from "./components/BarChart";

// Inside the return:
<VisualisationPanel>
  <BarChart
    data={[38, 27, 43, 3, 9, 82, 10]}
    highlightIndices={[2, 3]}
  />
</VisualisationPanel>
```

Visit `/algorithms`. You should see a bar chart with 7 bars, two of them highlighted in yellow/amber.

## 5.8 The margin convention

```tsx
const margin = { top: 20, right: 20, bottom: 30, left: 20 };
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

const g = svg
  .append("g")
  .attr("transform", `translate(${margin.left},${margin.top})`);
```

This is a D3 convention used in virtually every chart. The idea:

```
┌─────────────────────────────┐  ← SVG element (full width × height)
│  margin.top                 │
│  ┌─────────────────────┐   │
│  │                     │   │
│m │  Chart area         │ m │
│.l│  (innerWidth ×      │ .r│
│  │   innerHeight)      │   │
│  │                     │   │
│  └─────────────────────┘   │
│  margin.bottom              │
└─────────────────────────────┘
```

The `<g>` group is translated so that (0,0) is the top-left of the chart area. All drawing happens relative to this — no need to add margins to every coordinate.

> **Why not just make the SVG smaller?** Margins give space for axes, labels, and legends. Without them, bars would be cut off at the edges.

## Summary

✅ You understand SVG — HTML for graphics  
✅ You understand D3 selections and data binding  
✅ You understand scales — mapping data to pixels  
✅ You understand the margin convention  
✅ You have a working bar chart component  

## Key takeaway

**D3 is a data-to-DOM mapping library.** You give it data and tell it how to create/update/remove DOM elements to match. Scales translate between data space and pixel space. The margin convention gives breathing room around your chart.

---

→ [Chapter 06: Animating with D3](./06-ANIMATING-WITH-D3.md)
