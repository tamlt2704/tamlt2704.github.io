# Chapter 07: Adding Rough.js — Hand-Drawn Style

## What you'll learn

- How Rough.js works (it generates SVG paths that look hand-drawn)
- How to combine D3's data/layout with Rough.js's rendering
- The trade-off: Rough.js and D3 transitions
- A practical hybrid approach

## 7.1 What Rough.js does

Rough.js takes geometric shapes (rectangles, circles, lines) and renders them as if drawn by hand:

```
Normal SVG rect:          Rough.js rect:
┌──────────────┐          ╭──~───────~──╮
│              │          │    ~~        │
│              │          │        ~     ╎
│              │          ╎              │
└──────────────┘          ╰~────────~───╯
```

It adds imperfection — slightly wobbly lines, sketch-like fills. This makes diagrams feel less clinical and more approachable for learners.

## 7.2 How Rough.js works internally

Rough.js doesn't modify existing SVG elements. It CREATES new SVG path elements with intentionally imperfect coordinates. So you can't just add "roughness" to an existing `<rect>` — you have to draw with Rough.js from scratch.

```tsx
import rough from "roughjs";

// Get a Rough.js canvas (wraps an SVG element)
const rc = rough.svg(svgElement);

// Draw a rough rectangle — returns an SVG group element
const node = rc.rectangle(10, 10, 100, 60, {
  fill: "blue",
  fillStyle: "hachure",  // sketch-like fill
  roughness: 1.5,
});

// Append it to the SVG
svgElement.appendChild(node);
```

## 7.3 The challenge: Rough.js + D3 transitions

Here's the problem:

- **D3 transitions** animate attributes (`x`, `y`, `width`, `height`) smoothly
- **Rough.js** generates path data based on coordinates at render time

You can't transition a Rough.js element smoothly because its `d` attribute (the path data) is random — each render produces different wiggly paths. Transitioning between two random paths looks chaotic, not smooth.

**The solution: a hybrid approach.**

| Layer | Tool | Responsibility |
|-------|------|---------------|
| Background (static shapes) | Rough.js | Draw the bars with sketchy style |
| Animations (movement) | D3 | Translate/transform groups smoothly |
| Overlays (highlights) | D3 | Colour changes, opacity |

The trick: wrap each Rough.js shape in a `<g>` (group) element. Animate the group's `transform` attribute with D3. The shape inside moves with its parent — no need to re-render the paths.

## 7.4 Build a RoughBarChart component

Create `app/algorithms/components/RoughBarChart.tsx`:

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import rough from "roughjs";

type RoughBarChartProps = {
  data: number[];
  highlightIndices?: number[];
  width?: number;
  height?: number;
};

export default function RoughBarChart({
  data,
  highlightIndices = [],
  width = 500,
  height = 300,
}: RoughBarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = svgRef.current;
    const d3Svg = d3.select(svg);

    // Clear previous content
    d3Svg.selectAll("*").remove();

    const rc = rough.svg(svg);
    const margin = { top: 20, right: 20, bottom: 30, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = d3Svg
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

    // Draw bars with Rough.js
    data.forEach((value, index) => {
      const x = xScale(String(index)) || 0;
      const y = yScale(value);
      const barWidth = xScale.bandwidth();
      const barHeight = innerHeight - y;

      const isHighlighted = highlightIndices.includes(index);

      // Create a group for this bar (so we can animate the group)
      const barGroup = g.append("g")
        .attr("class", `bar-${index}`)
        .attr("transform", `translate(${x}, ${y})`);

      // Draw the rough rectangle
      const roughRect = rc.rectangle(0, 0, barWidth, barHeight, {
        fill: isHighlighted ? "#f59e0b" : "#3b82f6",
        fillStyle: "hachure",
        fillWeight: 2,
        hachureGap: 6,
        roughness: 1.2,
        stroke: isHighlighted ? "#d97706" : "#1d4ed8",
        strokeWidth: 1.5,
      });

      barGroup.node()!.appendChild(roughRect);

      // Add value label (regular SVG text — not rough)
      barGroup
        .append("text")
        .attr("x", barWidth / 2)
        .attr("y", -8)
        .attr("text-anchor", "middle")
        .attr("font-size", "13px")
        .attr("font-weight", "bold")
        .attr("fill", "#374151")
        .text(value);
    });
  }, [data, highlightIndices, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}
```

## 7.5 Understanding the Rough.js options

```tsx
rc.rectangle(x, y, width, height, {
  fill: "#3b82f6",        // fill colour
  fillStyle: "hachure",   // how to fill: hachure, solid, zigzag, cross-hatch, dots
  fillWeight: 2,          // line thickness of fill strokes
  hachureGap: 6,          // space between hachure lines
  roughness: 1.2,         // how "rough" the lines are (0 = perfect, 3+ = very rough)
  stroke: "#1d4ed8",      // outline colour
  strokeWidth: 1.5,       // outline thickness
});
```

**Fill styles compared:**

| Style | Look | Best for |
|-------|------|----------|
| `"hachure"` | Diagonal lines (like hand-drawn shading) | Default — looks most natural |
| `"solid"` | Solid colour with rough edges | When you need readable colours |
| `"zigzag"` | Zigzag fill pattern | Decorative |
| `"cross-hatch"` | Cross-hatched lines | Dense/important elements |
| `"dots"` | Dotted fill | Lighter/secondary elements |

> **Choosing roughness:** For algorithm visualisation, `roughness: 1.0–1.5` is the sweet spot. Too low (0.5) looks almost normal. Too high (3+) becomes illegible. The hand-drawn feel should add personality without reducing clarity.

## 7.6 Animating Rough.js bars

Since we can't transition Rough.js paths directly, we animate the parent `<g>` transform:

```tsx
// When data changes, update positions via transform
const barGroups = g.selectAll<SVGGElement, number>("g[class^='bar-']")
  .data(data);

barGroups
  .transition()
  .duration(400)
  .attr("transform", (_, i) => {
    const x = xScale(String(i)) || 0;
    const y = yScale(data[i]);
    return `translate(${x}, ${y})`;
  });
```

This moves the entire bar group (including the rough paths inside) to a new position smoothly. The rough shapes themselves don't change — they just ride along.

**For a swap animation:**
1. Calculate the target x positions
2. Animate both groups' transforms to swap their x values
3. After the animation completes, re-render with updated data (new rough paths at new positions)

## 7.7 When to use Rough.js vs plain D3

| Scenario | Recommendation |
|----------|---------------|
| Educational/tutorial site | Rough.js — approachable, whiteboard feel |
| Rapid animations (< 200ms between frames) | Plain D3 — Rough.js re-render is noticeable |
| Many elements (50+) | Plain D3 — Rough.js creates many path nodes per shape |
| Static diagrams | Rough.js — shines when shapes don't change often |
| Production analytics dashboard | Plain D3 — professional look expected |

For our algorithm visualiser, the best approach is:
- **Use Rough.js for the "resting" state** (bars sitting in place)
- **Use D3 transitions for movement** (transform the group)
- **Re-render Rough.js after animation completes** (settle into new positions)

## 7.8 Use the RoughBarChart

Update `page.tsx` to use the new component:

```tsx
import RoughBarChart from "./components/RoughBarChart";

// In the VisualisationPanel:
<VisualisationPanel>
  <RoughBarChart
    data={arrayData}
    highlightIndices={comparing}
  />
</VisualisationPanel>
```

You should now see hand-drawn style bars! They look like a whiteboard sketch.

## 7.9 Making it configurable (optional)

You might want both styles available. Add a toggle:

```tsx
const [useRoughStyle, setUseRoughStyle] = useState(true);

// In the JSX:
<VisualisationPanel>
  {useRoughStyle ? (
    <RoughBarChart data={arrayData} highlightIndices={comparing} />
  ) : (
    <BarChart data={arrayData} highlightIndices={comparing} swappingIndices={swapping} />
  )}
</VisualisationPanel>
```

## Summary

✅ You understand how Rough.js generates sketchy SVG paths  
✅ You know the limitation: can't smoothly transition Rough.js paths  
✅ You know the hybrid solution: animate the `<g>` wrapper, not the paths  
✅ You built a hand-drawn bar chart component  
✅ You know when to use Rough.js vs plain D3  

## Key takeaway

**Rough.js + D3 = use each for what it's best at.** D3 handles data binding, scales, and animations (via group transforms). Rough.js handles the visual rendering style. They complement each other — D3 is the brain, Rough.js is the pencil.

---

→ [Chapter 08: The Step Engine](./08-THE-STEP-ENGINE.md)
