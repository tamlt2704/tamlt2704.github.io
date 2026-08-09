# Chapter 17: Isometric Visualisation with Rough.js and D3

## What you'll learn

- What isometric projection is and the maths behind it
- How to transform 2D grid coordinates into isometric space
- How to draw isometric cubes, tiles, and stacked bars with Rough.js
- How to combine D3 data binding with isometric positioning
- How to build an isometric bar chart and grid map for algorithm visualisation

---

## PART 1: Isometric Fundamentals

## 17.1 What is isometric projection?

Normal 2D charts look flat. Isometric projection adds a 3D feel without perspective distortion — all lines stay parallel (no vanishing point). Think SimCity, Monument Valley, or Minecraft fan art.

```
Standard 2D view:          Isometric view:

┌─────┐                      ╱╲
│     │                    ╱    ╲
│     │                  ╱   ╱╲   ╲
└─────┘                  ╲ ╱    ╲ ╱
                           ╲    ╱
                             ╲╱
```

Isometric uses a fixed 30° angle (technically 26.57° = arctan(0.5), but we round). The x-axis goes down-right, the y-axis goes down-left, and the z-axis goes straight up.

## 17.2 The coordinate transformation

To convert a grid position `(col, row)` to isometric screen coordinates `(screenX, screenY)`:

```ts
function toIsometric(col: number, row: number, tileWidth: number, tileHeight: number) {
  const screenX = (col - row) * (tileWidth / 2);
  const screenY = (col + row) * (tileHeight / 2);
  return { screenX, screenY };
}
```

Where:
- `tileWidth` = width of a single diamond tile (typically 64px)
- `tileHeight` = height of a single diamond tile (typically 32px — half the width for true isometric)

To add a Z-axis (height/stacking):

```ts
function toIsometric3D(
  col: number,
  row: number,
  height: number,
  tileWidth: number,
  tileHeight: number
) {
  const screenX = (col - row) * (tileWidth / 2);
  const screenY = (col + row) * (tileHeight / 2) - height;
  return { screenX, screenY };
}
```

The `- height` lifts things up on screen (since SVG y-axis is inverted).

## 17.3 Drawing an isometric tile with Rough.js

A single isometric tile is a diamond (rhombus) made of 4 points:

```ts
function isoTilePoints(
  cx: number,
  cy: number,
  tileW: number,
  tileH: number
): [number, number][] {
  return [
    [cx, cy - tileH / 2],           // top
    [cx + tileW / 2, cy],           // right
    [cx, cy + tileH / 2],           // bottom
    [cx - tileW / 2, cy],           // left
  ];
}
```

Draw with Rough.js:

```tsx
import rough from "roughjs";

const rc = rough.svg(svgElement);
const points = isoTilePoints(200, 150, 64, 32);
const tile = rc.polygon(points, {
  fill: "skyblue",
  fillStyle: "hachure",
  stroke: "black",
  strokeWidth: 1,
  roughness: 1.2,
});
svgElement.appendChild(tile);
```

## 17.4 Drawing an isometric cube (3D block)

A cube has 3 visible faces: top, left, right.

```ts
function isoCubePoints(
  cx: number,
  cy: number,
  tileW: number,
  tileH: number,
  blockHeight: number
) {
  const hw = tileW / 2;
  const hh = tileH / 2;

  // Top face (diamond)
  const top: [number, number][] = [
    [cx, cy - hh - blockHeight],           // top
    [cx + hw, cy - blockHeight],           // right
    [cx, cy + hh - blockHeight],           // bottom
    [cx - hw, cy - blockHeight],           // left
  ];

  // Left face (parallelogram)
  const left: [number, number][] = [
    [cx - hw, cy - blockHeight],           // top-left
    [cx, cy + hh - blockHeight],           // top-right
    [cx, cy + hh],                         // bottom-right
    [cx - hw, cy],                         // bottom-left
  ];

  // Right face (parallelogram)
  const right: [number, number][] = [
    [cx + hw, cy - blockHeight],           // top-right
    [cx, cy + hh - blockHeight],           // top-left
    [cx, cy + hh],                         // bottom-left
    [cx + hw, cy],                         // bottom-right
  ];

  return { top, left, right };
}
```

Draw each face with different shading:

```tsx
const { top, left, right } = isoCubePoints(200, 200, 64, 32, 40);
const rc = rough.svg(svgElement);

// Right face (darkest)
svgElement.appendChild(rc.polygon(right, {
  fill: "#1e40af", fillStyle: "solid", stroke: "#1e3a5f",
}));

// Left face (medium)
svgElement.appendChild(rc.polygon(left, {
  fill: "#3b82f6", fillStyle: "solid", stroke: "#1e3a5f",
}));

// Top face (lightest)
svgElement.appendChild(rc.polygon(top, {
  fill: "#93c5fd", fillStyle: "solid", stroke: "#1e3a5f",
}));
```

> **Draw order matters!** Draw back-to-front (painter's algorithm). For an isometric grid, draw from top-left to bottom-right (row by row). This ensures closer tiles cover farther ones correctly.

## 17.5 Isometric grid — data binding with D3

Combine D3's data binding with isometric positioning:

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import rough from "roughjs";

type IsoGridProps = {
  data: number[][];  // 2D grid of values (height of each block)
  tileWidth?: number;
  tileHeight?: number;
};

export default function IsoGrid({ data, tileWidth = 64, tileHeight = 32 }: IsoGridProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const svg = svgRef.current;
    svg.innerHTML = "";

    const rc = rough.svg(svg);
    const rows = data.length;
    const cols = data[0]?.length || 0;

    // Center the grid in the SVG
    const offsetX = 400;
    const offsetY = 100;

    // Draw back-to-front for correct overlap
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const value = data[row][col];
        const blockHeight = value * 8; // Scale value to pixel height

        // Convert to isometric screen position
        const screenX = offsetX + (col - row) * (tileWidth / 2);
        const screenY = offsetY + (col + row) * (tileHeight / 2);

        // Draw base tile
        const tilePoints = isoTilePoints(screenX, screenY, tileWidth, tileHeight);
        svg.appendChild(rc.polygon(tilePoints, {
          fill: "#e2e8f0",
          fillStyle: "solid",
          stroke: "#94a3b8",
          strokeWidth: 0.5,
        }));

        // Draw block if value > 0
        if (blockHeight > 0) {
          const { top, left, right } = isoCubePoints(
            screenX, screenY, tileWidth, tileHeight, blockHeight
          );

          // Use D3 colour scale for value
          const colour = d3.interpolateBlues(value / d3.max(data.flat())!);
          const colourDark = d3.color(colour)?.darker(0.5)?.toString() || "#1e40af";
          const colourLight = d3.color(colour)?.brighter(0.3)?.toString() || "#93c5fd";

          svg.appendChild(rc.polygon(right, {
            fill: colourDark, fillStyle: "solid", stroke: "#1e293b", strokeWidth: 0.5,
          }));
          svg.appendChild(rc.polygon(left, {
            fill: colour, fillStyle: "solid", stroke: "#1e293b", strokeWidth: 0.5,
          }));
          svg.appendChild(rc.polygon(top, {
            fill: colourLight, fillStyle: "solid", stroke: "#1e293b", strokeWidth: 0.5,
          }));
        }
      }
    }
  }, [data, tileWidth, tileHeight]);

  return <svg ref={svgRef} width={800} height={500} />;
}

// Helper functions (defined above, included here for completeness)
function isoTilePoints(cx: number, cy: number, tw: number, th: number): [number, number][] {
  return [
    [cx, cy - th / 2],
    [cx + tw / 2, cy],
    [cx, cy + th / 2],
    [cx - tw / 2, cy],
  ];
}

function isoCubePoints(cx: number, cy: number, tw: number, th: number, h: number) {
  const hw = tw / 2, hh = th / 2;
  return {
    top: [[cx, cy - hh - h], [cx + hw, cy - h], [cx, cy + hh - h], [cx - hw, cy - h]] as [number, number][],
    left: [[cx - hw, cy - h], [cx, cy + hh - h], [cx, cy + hh], [cx - hw, cy]] as [number, number][],
    right: [[cx + hw, cy - h], [cx, cy + hh - h], [cx, cy + hh], [cx + hw, cy]] as [number, number][],
  };
}
```

## 17.6 Isometric bar chart (sorting algorithms)

Instead of flat bars, show sorting as isometric columns:

```tsx
function IsoBarChart({ data, highlightIndices = [] }: { data: number[]; highlightIndices?: number[] }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const svg = svgRef.current;
    svg.innerHTML = "";
    const rc = rough.svg(svg);

    const tileW = 48;
    const tileH = 24;
    const offsetX = 300;
    const offsetY = 250;
    const maxVal = Math.max(...data);

    data.forEach((value, col) => {
      const blockHeight = (value / maxVal) * 150;
      const screenX = offsetX + col * (tileW * 0.8); // slight overlap for depth
      const screenY = offsetY + col * (tileH * 0.4);

      const isHighlighted = highlightIndices.includes(col);
      const baseColour = isHighlighted ? "#f59e0b" : "#3b82f6";
      const darkColour = isHighlighted ? "#d97706" : "#1d4ed8";
      const lightColour = isHighlighted ? "#fcd34d" : "#93c5fd";

      const { top, left, right } = isoCubePoints(screenX, screenY, tileW, tileH, blockHeight);

      svg.appendChild(rc.polygon(right, {
        fill: darkColour, fillStyle: "solid", stroke: "#0f172a", roughness: 0.8,
      }));
      svg.appendChild(rc.polygon(left, {
        fill: baseColour, fillStyle: "solid", stroke: "#0f172a", roughness: 0.8,
      }));
      svg.appendChild(rc.polygon(top, {
        fill: lightColour, fillStyle: "solid", stroke: "#0f172a", roughness: 0.8,
      }));

      // Value label on top
      const labelY = screenY - tileH / 2 - blockHeight - 10;
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", String(screenX));
      text.setAttribute("y", String(labelY));
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("font-size", "12");
      text.setAttribute("fill", "#374151");
      text.textContent = String(value);
      svg.appendChild(text);
    });
  }, [data, highlightIndices]);

  return <svg ref={svgRef} width={600} height={350} />;
}
```

## 17.7 Rough.js fill styles for visual variety

Rough.js offers multiple fill patterns:

| `fillStyle` | Look | Best for |
|-------------|------|----------|
| `"solid"` | Flat colour | Clean isometric blocks |
| `"hachure"` | Diagonal lines | Sketchy/hand-drawn feel |
| `"zigzag"` | Zigzag lines | Textured surfaces |
| `"cross-hatch"` | Cross pattern | Dense shading |
| `"dots"` | Dotted fill | Light/empty areas |

```tsx
rc.polygon(points, {
  fill: "#3b82f6",
  fillStyle: "hachure",     // try different styles
  hachureAngle: 60,         // angle of hachure lines
  hachureGap: 4,            // spacing between lines
  roughness: 1.5,           // how wobbly lines are (0 = straight, 3 = very rough)
  strokeWidth: 1.5,
});
```

## 17.8 Animation — growing isometric blocks

Animate blocks growing by interpolating height over time:

```tsx
useEffect(() => {
  if (!svgRef.current) return;
  let frame: number;
  let progress = 0;

  function animate() {
    progress = Math.min(progress + 0.02, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic

    // Redraw with height scaled by eased progress
    drawIsoGrid(data, eased);

    if (progress < 1) {
      frame = requestAnimationFrame(animate);
    }
  }

  frame = requestAnimationFrame(animate);
  return () => cancelAnimationFrame(frame);
}, [data]);
```

> **Note:** Rough.js redraws produce slightly different wobble each frame (because randomness). For smooth animation, generate the rough paths ONCE, then transform/scale them. Or use `seed` option: `rc.polygon(points, { seed: 42 })` — same seed = same wobble.

## Summary

✅ You understand isometric coordinate transformation (col, row → screenX, screenY)
✅ You can draw isometric tiles, cubes, and stacked blocks
✅ You know the draw order (painter's algorithm — back to front)
✅ You combined D3 colour scales with Rough.js fill styles
✅ You built an isometric bar chart and grid visualisation
✅ You know how to animate isometric blocks with `requestAnimationFrame`

## Key takeaways

**Isometric is just a coordinate transform.** `screenX = (col - row) * halfWidth`, `screenY = (col + row) * halfHeight`. Everything else is drawing faces in the right order.

**Rough.js adds character.** The hand-drawn aesthetic makes visualisations feel friendly and approachable — perfect for educational content. Use `seed` for deterministic output.

**D3 + Rough.js + Isometric** = data-driven hand-drawn 3D visualisations. D3 handles the data/scales, isometric handles the projection, Rough.js handles the rendering style.

---

→ [Chapter 18: Three.js — Real 3D in the Browser](./18-THREEJS-FUNDAMENTALS.md)
