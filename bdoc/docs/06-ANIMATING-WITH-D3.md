# Chapter 06: Animating with D3

## What you'll learn

- How D3 transitions animate between states
- The enter/update/exit pattern (data changes over time)
- How to animate a swap (two bars trading places)
- How to keep D3 in sync with React state

## 6.1 What is a D3 transition?

A transition smoothly changes an attribute from its current value to a new value over time:

```tsx
// Instant: bar jumps to new position
rect.attr("x", 200);

// Animated: bar slides to new position over 500ms
rect.transition().duration(500).attr("x", 200);
```

That's it. Add `.transition().duration(ms)` before your `.attr()` calls, and D3 interpolates the values.

> **How does it work internally?** D3 starts a timer. On each frame (~60fps), it calculates the intermediate value between the start and end, and updates the DOM. When 500ms have passed, it sets the final value exactly. This is smoother than CSS transitions for SVG because D3 can interpolate complex values (colours, paths, transforms).
>
> **Alternative: CSS transitions.** You can animate SVG with `transition: all 0.5s` in CSS. It works for simple cases (colour, opacity, transform) but breaks for SVG-specific attributes like `d` (path data) or coordinated multi-element animations. D3 transitions handle all of these.

## 6.2 Update BarChart to animate

Replace the content of `app/algorithms/components/BarChart.tsx`:

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

type BarChartProps = {
  data: number[];
  highlightIndices?: number[];
  swappingIndices?: [number, number] | null;
  width?: number;
  height?: number;
};

export default function BarChart({
  data,
  highlightIndices = [],
  swappingIndices = null,
  width = 500,
  height = 300,
}: BarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const initialised = useRef(false);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const margin = { top: 20, right: 20, bottom: 30, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Only create the group once
    let g = svg.select<SVGGElement>("g.chart-area");
    if (g.empty()) {
      g = svg
        .append("g")
        .attr("class", "chart-area")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    }

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

    // DATA JOIN — the enter/update/exit pattern
    const bars = g.selectAll<SVGRectElement, number>("rect").data(data);

    // ENTER: new bars that don't exist yet
    const barsEnter = bars
      .enter()
      .append("rect")
      .attr("x", (_, i) => xScale(String(i)) || 0)
      .attr("y", innerHeight) // start at bottom
      .attr("width", xScale.bandwidth())
      .attr("height", 0) // start with no height
      .attr("rx", 4);

    // UPDATE + ENTER merged: animate all bars to their correct position
    bars
      .merge(barsEnter)
      .transition()
      .duration(400)
      .attr("x", (_, i) => xScale(String(i)) || 0)
      .attr("y", (d) => yScale(d))
      .attr("width", xScale.bandwidth())
      .attr("height", (d) => innerHeight - yScale(d))
      .attr("fill", (_, i) => {
        if (swappingIndices && (i === swappingIndices[0] || i === swappingIndices[1])) {
          return "#ef4444"; // red for swapping
        }
        if (highlightIndices.includes(i)) {
          return "#f59e0b"; // amber for comparing
        }
        return "#3b82f6"; // blue default
      });

    // EXIT: remove bars that no longer have data
    bars.exit().transition().duration(300).attr("height", 0).attr("y", innerHeight).remove();

    // Value labels
    const labels = g.selectAll<SVGTextElement, number>("text.value-label").data(data);

    const labelsEnter = labels
      .enter()
      .append("text")
      .attr("class", "value-label")
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#374151");

    labels
      .merge(labelsEnter)
      .transition()
      .duration(400)
      .attr("x", (_, i) => (xScale(String(i)) || 0) + xScale.bandwidth() / 2)
      .attr("y", (d) => yScale(d) - 5)
      .text((d) => d);

    labels.exit().remove();
  }, [data, highlightIndices, swappingIndices, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}
```

## 6.3 The enter/update/exit pattern — in detail

This is D3's most powerful (and initially confusing) concept. Here's the mental model:

**Imagine a parking lot with numbered spaces:**

```
Frame 1: data = [5, 3, 8]
  Space 0: [rect showing 5]
  Space 1: [rect showing 3]
  Space 2: [rect showing 8]

Frame 2: data = [5, 8, 3, 2]  (swapped, added one)
  Space 0: [update] still showing 5
  Space 1: [update] was 3, now 8 — animate height change
  Space 2: [update] was 8, now 3 — animate height change
  Space 3: [enter] new! create rect, animate in
```

```tsx
const bars = g.selectAll("rect").data(data);
// bars = the "update" selection (existing elements matched to new data)

bars.enter()   // elements that NEED to be created
bars.exit()    // elements that NEED to be removed
bars.merge(barsEnter)  // all elements (existing + new) together
```

> **Why is this so different from React?** React abstracts this away — you return JSX and React figures out what to add/remove/update. D3 makes it explicit because you need control over the ANIMATIONS between states. In React, an element "jumps" to its new state. In D3, you choreograph HOW it transitions.

## 6.4 The key difference: `svg.selectAll("*").remove()` vs enter/update/exit

In Chapter 05, we cleared everything on each render:

```tsx
svg.selectAll("*").remove(); // nuke everything, redraw from scratch
```

Now we use the enter/update/exit pattern. Why?

| Approach | Pros | Cons |
|----------|------|------|
| Clear + redraw | Simple, no bugs | No animations possible — elements are destroyed and recreated |
| Enter/update/exit | Smooth animations between states | More complex code |

For algorithm visualisation, animations are essential — they show what's changing. So we need the update pattern.

## 6.5 Testing the animation

Update `page.tsx` to change data on button press:

```tsx
const [arrayData, setArrayData] = useState([38, 27, 43, 3, 9, 82, 10]);
const [comparing, setComparing] = useState<number[]>([]);
const [swapping, setSwapping] = useState<[number, number] | null>(null);

// Replace the VisualisationPanel content:
<VisualisationPanel>
  <BarChart
    data={arrayData}
    highlightIndices={comparing}
    swappingIndices={swapping}
  />
</VisualisationPanel>
```

Now try adding a test button temporarily:

```tsx
<button
  onClick={() => {
    const newData = [...arrayData];
    // Swap first two elements
    [newData[0], newData[1]] = [newData[1], newData[0]];
    setSwapping([0, 1]);
    setTimeout(() => {
      setArrayData(newData);
      setSwapping(null);
    }, 500);
  }}
  className="px-3 py-1 bg-gray-200 rounded"
>
  Test Swap
</button>
```

Click it — you should see the first two bars swap positions with a smooth animation, flashing red during the swap.

## 6.6 Easing functions

By default, transitions use "cubic" easing — they start slow, speed up, and slow down at the end. You can change this:

```tsx
.transition()
.duration(400)
.ease(d3.easeBounceOut)  // bouncy effect
```

Common easing options:

| Easing | Effect | Best for |
|--------|--------|----------|
| `d3.easeLinear` | Constant speed | Continuous motion |
| `d3.easeCubicInOut` | Smooth accel/decel (default) | General use |
| `d3.easeBounceOut` | Bounces at the end | Playful/educational |
| `d3.easeElasticOut` | Springy overshoot | Attention-grabbing |
| `d3.easeBackOut` | Slight overshoot then settle | Subtle emphasis |

For algorithm visualisation, the default cubic is usually best — it's smooth and professional. Bounce can be fun for the educational context.

## 6.7 Sequencing transitions

For a swap animation, you want:
1. Highlight both bars (amber) — 200ms
2. Turn them red — 200ms
3. Swap positions — 400ms
4. Turn them blue — 200ms

D3 supports chaining with `.transition()`:

```tsx
bar
  .transition().duration(200).attr("fill", "#f59e0b")  // amber
  .transition().duration(200).attr("fill", "#ef4444")  // red
  .transition().duration(400).attr("x", newX)          // move
  .transition().duration(200).attr("fill", "#3b82f6"); // blue
```

Each `.transition()` after the first waits for the previous one to finish.

We'll use this technique in Chapter 08 when we build the step engine.

## Summary

✅ You understand D3 transitions (`.transition().duration().attr()`)  
✅ You understand enter/update/exit (creating, updating, removing elements)  
✅ You can animate bars changing position, height, and colour  
✅ You know about easing functions and transition sequencing  

## Key takeaway

**D3 transitions are what make algorithm visualisation alive.** Without them, data changes are instantaneous — you can't see what happened. Transitions let the user SEE the operation: "those two bars swapped", "that node was visited". The enter/update/exit pattern is the mechanism that makes this work.

---

→ [Chapter 07: Adding Rough.js — Hand-Drawn Style](./07-ADDING-ROUGHJS.md)
