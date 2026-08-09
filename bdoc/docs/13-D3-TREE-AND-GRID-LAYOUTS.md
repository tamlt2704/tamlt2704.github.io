# Chapter 13: D3 Tree Layout and Grid Layout

## What you'll learn

- How `d3.hierarchy()` converts flat data into a tree structure
- How `d3.tree()` positions nodes in a clean hierarchical layout
- How to draw links (edges) between parent and child nodes
- How to build a grid layout for matrix-based algorithm visualisation
- When to use tree vs force vs grid layouts

## 13.1 When to use which layout

You already know **force layout** from Chapter 10 — nodes repel each other and links act as springs. It's general-purpose but produces a different arrangement every time.

| Layout | Best for | Positioning | Deterministic? |
|--------|----------|-------------|----------------|
| Force | Arbitrary graphs, networks | Physics simulation | No — varies per run |
| Tree | Hierarchies, recursion trees, DOM trees | Algorithmic (Reingold-Tilford) | Yes — same data, same layout |
| Grid | Matrices, 2D arrays, dynamic programming tables | Row × Column formula | Yes — deterministic |

**Tree layout** is perfect for:
- Recursion trees (fibonacci, merge sort)
- Binary search trees
- File system visualisation
- DOM tree inspection
- Parse trees

**Grid layout** is perfect for:
- Dynamic programming tables
- Matrix traversal (BFS on a grid)
- Game boards (chess, tic-tac-toe)
- Heatmaps of algorithm state

---

## PART 1: D3 Tree Layout

## 13.2 Understanding hierarchical data

D3's tree layout requires a specific data shape: a root node with children.

```ts
// Hierarchical data — what d3.hierarchy expects
const treeData = {
  name: "fib(5)",
  children: [
    {
      name: "fib(4)",
      children: [
        { name: "fib(3)", children: [
          { name: "fib(2)", children: [{ name: "fib(1)" }, { name: "fib(0)" }] },
          { name: "fib(1)" },
        ]},
        { name: "fib(2)", children: [{ name: "fib(1)" }, { name: "fib(0)" }] },
      ],
    },
    {
      name: "fib(3)",
      children: [
        { name: "fib(2)", children: [{ name: "fib(1)" }, { name: "fib(0)" }] },
        { name: "fib(1)" },
      ],
    },
  ],
};
```

`d3.hierarchy()` converts this into a tree structure with computed properties:

```ts
const root = d3.hierarchy(treeData);
// root.depth = 0, root.height = 4
// root.children[0].depth = 1
// root.descendants() — all nodes as a flat array
// root.links() — all parent→child connections
```

> **What if my data is flat (like an adjacency list)?** You'll need to convert it first. D3 provides `d3.stratify()` for that:
> ```ts
> const flat = [
>   { id: "root", parentId: null },
>   { id: "child1", parentId: "root" },
>   { id: "child2", parentId: "root" },
> ];
> const root = d3.stratify()
>   .id(d => d.id)
>   .parentId(d => d.parentId)(flat);
> ```

## 13.3 The d3.tree() layout

`d3.tree()` assigns x,y coordinates to every node in the hierarchy:

```ts
const treeLayout = d3.tree<TreeNode>().size([width, height]);
const root = d3.hierarchy(treeData);
treeLayout(root);

// Now every node has .x and .y set:
// root.x = 250, root.y = 0
// root.children[0].x = 125, root.children[0].y = 100
```

The algorithm (Reingold-Tilford) ensures:
1. Parent is centered above its children
2. No nodes overlap
3. The tree is as compact as possible
4. Symmetric subtrees produce symmetric layouts

> **`size` vs `nodeSize`:**
> - `.size([width, height])` — fit the entire tree into this bounding box
> - `.nodeSize([dx, dy])` — each node gets this much space; tree may exceed the SVG bounds
>
> Use `.size()` when you want the tree to fill a known area. Use `.nodeSize()` when you want consistent spacing regardless of tree depth.

## 13.4 Build the TreeChart component

Create `app/algorithms/components/TreeChart.tsx`:

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

type TreeNodeData = {
  name: string;
  value?: number;
  children?: TreeNodeData[];
};

type TreeChartProps = {
  data: TreeNodeData;
  highlightNodes?: string[];        // node names to highlight
  currentNode?: string | null;      // currently active node
  width?: number;
  height?: number;
};

export default function TreeChart({
  data,
  highlightNodes = [],
  currentNode = null,
  width = 600,
  height = 400,
}: TreeChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 40, right: 40, bottom: 40, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // 1. Create hierarchy from data
    const root = d3.hierarchy(data);

    // 2. Apply tree layout — assigns x,y to each node
    const treeLayout = d3.tree<TreeNodeData>().size([innerWidth, innerHeight]);
    treeLayout(root);

    // 3. Draw links (parent → child edges)
    g.selectAll("path.link")
      .data(root.links())
      .enter()
      .append("path")
      .attr("class", "link")
      .attr("d", (d) => {
        // Curved link from parent to child
        return `M${d.source.x},${d.source.y}
                C${d.source.x},${(d.source.y + d.target.y) / 2}
                 ${d.target.x},${(d.source.y + d.target.y) / 2}
                 ${d.target.x},${d.target.y}`;
      })
      .attr("fill", "none")
      .attr("stroke", "#94a3b8")
      .attr("stroke-width", 1.5);

    // 4. Draw nodes
    const nodes = g
      .selectAll("g.node")
      .data(root.descendants())
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", (d) => `translate(${d.x},${d.y})`);

    // Circle for each node
    nodes
      .append("circle")
      .attr("r", 18)
      .attr("fill", (d) => {
        if (d.data.name === currentNode) return "#ef4444";       // red = active
        if (highlightNodes.includes(d.data.name)) return "#fbbf24"; // yellow = highlight
        return "#3b82f6";                                          // blue = default
      })
      .attr("stroke", "#1e293b")
      .attr("stroke-width", 2);

    // Label inside each node
    nodes
      .append("text")
      .text((d) => d.data.name)
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("font-size", "10px")
      .attr("font-weight", "bold")
      .attr("fill", "white");
  }, [data, highlightNodes, currentNode, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}
```

## 13.5 Understanding the link path

The curved link is drawn with a cubic Bézier curve (`C` command):

```
M source.x, source.y          ← Move to parent
C source.x, midY              ← Control point 1 (straight down from parent)
  target.x, midY              ← Control point 2 (straight up from child)
  target.x, target.y          ← End at child
```

This produces a smooth S-curve connecting parent to child. D3 also provides `d3.linkVertical()` as a shorthand:

```tsx
const linkGenerator = d3.linkVertical<
  d3.HierarchyPointLink<TreeNodeData>,
  d3.HierarchyPointNode<TreeNodeData>
>()
  .x((d) => d.x)
  .y((d) => d.y);

// Then use:
.attr("d", linkGenerator)
```

Both produce the same result. The explicit `C` path gives you more control over the curve shape.

> **Straight lines instead of curves?** Just use:
> ```tsx
> .attr("d", d => `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`)
> ```
> Straight lines work but look cluttered when subtrees overlap horizontally.

## 13.6 Horizontal tree (left-to-right)

Sometimes a horizontal tree is more readable (like a file explorer). Just swap x and y:

```tsx
const treeLayout = d3.tree<TreeNodeData>().size([innerHeight, innerWidth]);
//                                              ↑ height first, width second

// When positioning:
.attr("transform", (d) => `translate(${d.y},${d.x})`)
//                                     ↑ swap x and y

// Links also swap:
.attr("d", (d) => {
  return `M${d.source.y},${d.source.x}
          C${(d.source.y + d.target.y) / 2},${d.source.x}
           ${(d.source.y + d.target.y) / 2},${d.target.x}
           ${d.target.y},${d.target.x}`;
})
```

The tree layout always treats the first dimension as "across" and the second as "down". By swapping when rendering, you rotate the whole tree 90°.

## 13.7 Tree step type for algorithm visualisation

Define a step type for tree-based algorithms:

```ts
// In app/algorithms/lib/types.ts
export type TreeStep = {
  codeLine: number;
  description: string;
  tree: TreeNodeData;          // the full tree structure
  highlightNodes: string[];    // nodes to highlight (e.g., visited)
  currentNode: string | null;  // node being processed
  returnValue?: string;        // value being returned (for recursion)
};
```

Example: visualising recursive Fibonacci:

```ts
const steps: TreeStep[] = [
  {
    codeLine: 0,
    description: "Call fib(4)",
    tree: { name: "fib(4)", children: [] },
    highlightNodes: [],
    currentNode: "fib(4)",
  },
  {
    codeLine: 2,
    description: "fib(4) calls fib(3) and fib(2)",
    tree: {
      name: "fib(4)",
      children: [{ name: "fib(3)" }, { name: "fib(2)" }],
    },
    highlightNodes: [],
    currentNode: "fib(4)",
  },
  // ... more steps as the recursion unfolds
];
```

## 13.8 Animating tree growth

To animate a tree growing as recursion unfolds, use D3 transitions:

```tsx
// Initial state: all nodes start at parent position
nodes
  .attr("transform", (d) => {
    const parent = d.parent || d;
    return `translate(${parent.x},${parent.y})`;
  })
  .attr("opacity", 0)
  // Animate to final position
  .transition()
  .duration(500)
  .attr("transform", (d) => `translate(${d.x},${d.y})`)
  .attr("opacity", 1);
```

Links grow from parent to child:

```tsx
links
  .attr("d", (d) => {
    // Start: zero-length path at parent
    return `M${d.source.x},${d.source.y}
            C${d.source.x},${d.source.y}
             ${d.source.x},${d.source.y}
             ${d.source.x},${d.source.y}`;
  })
  .transition()
  .duration(500)
  .attr("d", (d) => {
    // End: full curve to child
    return `M${d.source.x},${d.source.y}
            C${d.source.x},${(d.source.y + d.target.y) / 2}
             ${d.target.x},${(d.source.y + d.target.y) / 2}
             ${d.target.x},${d.target.y}`;
  });
```

---

## PART 2: D3 Grid Layout

## 13.9 What is a grid layout?

A grid layout places elements in a row × column matrix. Unlike force or tree layouts, the position formula is trivial:

```
x = column * cellWidth
y = row * cellHeight
```

No simulation, no algorithm — just arithmetic. But D3 helps with colouring (scales), labelling, and interactivity.

**Use cases for algorithm visualisation:**
- Dynamic programming tables (knapsack, edit distance, longest common subsequence)
- Matrix traversal (BFS/DFS on a grid, pathfinding)
- Comparison matrices (sorting network diagrams)
- Game state boards

## 13.10 Define grid data types

```ts
// In app/algorithms/lib/types.ts
export type GridCell = {
  row: number;
  col: number;
  value: number | string;
  state?: "default" | "active" | "computed" | "path" | "highlighted";
};

export type GridStep = {
  codeLine: number;
  description: string;
  grid: GridCell[];             // flat array of cells
  rows: number;
  cols: number;
  currentCell?: [number, number] | null;  // [row, col] being processed
  formula?: string;            // e.g., "dp[i][j] = dp[i-1][j] + dp[i][j-1]"
};
```

## 13.11 Build the GridChart component

Create `app/algorithms/components/GridChart.tsx`:

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

type GridCell = {
  row: number;
  col: number;
  value: number | string;
  state?: "default" | "active" | "computed" | "path" | "highlighted";
};

type GridChartProps = {
  cells: GridCell[];
  rows: number;
  cols: number;
  currentCell?: [number, number] | null;
  width?: number;
  height?: number;
};

const STATE_COLOURS: Record<string, string> = {
  default: "#e2e8f0",      // slate-200
  active: "#ef4444",       // red-500
  computed: "#3b82f6",     // blue-500
  path: "#22c55e",         // green-500
  highlighted: "#fbbf24",  // amber-400
};

export default function GridChart({
  cells,
  rows,
  cols,
  currentCell = null,
  width = 500,
  height = 400,
}: GridChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 30, right: 20, bottom: 20, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Calculate cell size
    const cellWidth = innerWidth / cols;
    const cellHeight = innerHeight / rows;
    const cellSize = Math.min(cellWidth, cellHeight);

    // Draw cells
    const cellGroups = g
      .selectAll("g.cell")
      .data(cells)
      .enter()
      .append("g")
      .attr("class", "cell")
      .attr("transform", (d) => `translate(${d.col * cellSize},${d.row * cellSize})`);

    // Cell rectangle
    cellGroups
      .append("rect")
      .attr("width", cellSize - 2)
      .attr("height", cellSize - 2)
      .attr("rx", 4)
      .attr("fill", (d) => {
        // Current cell gets special treatment
        if (currentCell && d.row === currentCell[0] && d.col === currentCell[1]) {
          return STATE_COLOURS.active;
        }
        return STATE_COLOURS[d.state || "default"];
      })
      .attr("stroke", (d) => {
        if (currentCell && d.row === currentCell[0] && d.col === currentCell[1]) {
          return "#991b1b";
        }
        return "#94a3b8";
      })
      .attr("stroke-width", (d) => {
        if (currentCell && d.row === currentCell[0] && d.col === currentCell[1]) {
          return 3;
        }
        return 1;
      });

    // Cell value text
    cellGroups
      .append("text")
      .text((d) => String(d.value))
      .attr("x", (cellSize - 2) / 2)
      .attr("y", (cellSize - 2) / 2)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("font-size", Math.min(cellSize * 0.35, 14) + "px")
      .attr("font-weight", "bold")
      .attr("fill", (d) => {
        const state = d.state || "default";
        return state === "default" ? "#374151" : "white";
      });

    // Row labels (left side)
    for (let r = 0; r < rows; r++) {
      g.append("text")
        .text(String(r))
        .attr("x", -15)
        .attr("y", r * cellSize + cellSize / 2)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("font-size", "11px")
        .attr("fill", "#64748b");
    }

    // Column labels (top)
    for (let c = 0; c < cols; c++) {
      g.append("text")
        .text(String(c))
        .attr("x", c * cellSize + cellSize / 2)
        .attr("y", -12)
        .attr("text-anchor", "middle")
        .attr("font-size", "11px")
        .attr("fill", "#64748b");
    }
  }, [cells, rows, cols, currentCell, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}
```

## 13.12 Understanding the grid positioning

The key insight: grid layout is pure arithmetic, no D3 layout algorithm needed.

```
Cell at (row=2, col=3):
  x = 3 * cellSize = 3 * 50 = 150px
  y = 2 * cellSize = 2 * 50 = 100px
```

D3's role in a grid visualisation is:
1. **Data binding** — one rect per cell
2. **Colour scales** — map values to colours (e.g., heatmap)
3. **Transitions** — animate cell state changes
4. **Interactivity** — hover/click on cells

> **Why not just use CSS Grid?** You could render a grid with `<div>` elements and CSS `grid-template-columns`. For a static table, that's simpler. But SVG gives you:
> - Smooth colour transitions between steps
> - Arrows/lines between cells (showing dependencies)
> - Consistent rendering with your other D3 visualisations
> - No layout reflow when animating

## 13.13 Example: Dynamic programming table

Here's how to generate steps for a DP grid (e.g., edit distance):

```ts
export function generateDpGridSteps(
  word1: string,
  word2: string
): GridStep[] {
  const steps: GridStep[] = [];
  const rows = word1.length + 1;
  const cols = word2.length + 1;

  // Initialise DP table
  const dp: number[][] = Array.from({ length: rows }, () =>
    Array(cols).fill(0)
  );

  // Base cases
  for (let i = 0; i <= word1.length; i++) dp[i][0] = i;
  for (let j = 0; j <= word2.length; j++) dp[0][j] = j;

  // Convert to GridCell format
  function toGridCells(
    active?: [number, number],
    computed?: Set<string>
  ): GridCell[] {
    const cells: GridCell[] = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        let state: GridCell["state"] = "default";
        const key = `${r},${c}`;
        if (active && r === active[0] && c === active[1]) state = "active";
        else if (computed?.has(key)) state = "computed";
        cells.push({ row: r, col: c, value: dp[r][c], state });
      }
    }
    return cells;
  }

  const computed = new Set<string>();

  // Base case step
  for (let i = 0; i <= word1.length; i++) computed.add(`${i},0`);
  for (let j = 0; j <= word2.length; j++) computed.add(`0,${j}`);

  steps.push({
    codeLine: 2,
    description: "Initialise base cases: dp[i][0] = i, dp[0][j] = j",
    grid: toGridCells(undefined, computed),
    rows,
    cols,
    currentCell: null,
  });

  // Fill table
  for (let i = 1; i <= word1.length; i++) {
    for (let j = 1; j <= word2.length; j++) {
      if (word1[i - 1] === word2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = 1 + Math.min(
          dp[i - 1][j],     // delete
          dp[i][j - 1],     // insert
          dp[i - 1][j - 1]  // replace
        );
      }

      computed.add(`${i},${j}`);

      steps.push({
        codeLine: 8,
        description: `Computing dp[${i}][${j}] = ${dp[i][j]}`,
        grid: toGridCells([i, j], computed),
        rows,
        cols,
        currentCell: [i, j],
        formula: `dp[${i}][${j}] = ${dp[i][j]}`,
      });
    }
  }

  return steps;
}
```

## 13.14 Adding arrows to the grid (dependency visualisation)

For DP problems, showing which cells contribute to the current cell is powerful:

```tsx
// After drawing cells, draw arrows showing dependencies
if (currentCell) {
  const [row, col] = currentCell;
  const dependencies = [
    [row - 1, col],     // from above (delete)
    [row, col - 1],     // from left (insert)
    [row - 1, col - 1], // from diagonal (replace/match)
  ];

  // Add arrow marker
  svg.append("defs")
    .append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "0 0 10 10")
    .attr("refX", 5)
    .attr("refY", 5)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto-start-reverse")
    .append("path")
    .attr("d", "M 0 0 L 10 5 L 0 10 z")
    .attr("fill", "#ef4444");

  dependencies.forEach(([r, c]) => {
    if (r >= 0 && c >= 0) {
      g.append("line")
        .attr("x1", c * cellSize + cellSize / 2)
        .attr("y1", r * cellSize + cellSize / 2)
        .attr("x2", col * cellSize + cellSize / 2)
        .attr("y2", row * cellSize + cellSize / 2)
        .attr("stroke", "#ef4444")
        .attr("stroke-width", 2)
        .attr("marker-end", "url(#arrowhead)")
        .attr("opacity", 0.7);
    }
  });
}
```

## 13.15 Colour scale for heatmaps

For large grids, colour the cells by value intensity:

```tsx
// Create a sequential colour scale
const maxValue = d3.max(cells, (d) => Number(d.value)) || 1;
const colourScale = d3
  .scaleSequential(d3.interpolateBlues)
  .domain([0, maxValue]);

// Use in cell fill:
.attr("fill", (d) => {
  if (d.state === "active") return STATE_COLOURS.active;
  if (d.state === "computed") return colourScale(Number(d.value));
  return STATE_COLOURS.default;
})
```

This creates a gradient from light blue (low values) to dark blue (high values), making patterns in the DP table immediately visible.

---

## 13.16 Combining tree and grid

Some algorithms use BOTH layouts. For example:
- **Merge sort**: a tree (recursion) + an array (merging)
- **Segment trees**: a tree (structure) + an array (underlying data)
- **Trie**: a tree (structure) + a grid (search state)

You can render both in the same `VisualisationPanel` by splitting the SVG area:

```tsx
<VisualisationPanel>
  <div className="flex flex-col gap-2 h-full">
    <TreeChart data={step.tree} currentNode={step.activeNode} height={200} />
    <GridChart cells={step.grid} rows={step.rows} cols={step.cols} height={200} />
  </div>
</VisualisationPanel>
```

## 13.17 Integrating with the page

Add tree/grid algorithm detection to your page:

```tsx
// In page.tsx
const getVisualisationType = (algorithm: string) => {
  if (["bfs", "dfs"].includes(algorithm)) return "graph";
  if (["fibonacci", "bst"].includes(algorithm)) return "tree";
  if (["editDistance", "knapsack", "gridBfs"].includes(algorithm)) return "grid";
  return "bars"; // sorting algorithms
};

// In the render:
{visualisationType === "tree" && (
  <TreeChart
    data={step.tree}
    highlightNodes={step.highlightNodes}
    currentNode={step.currentNode}
  />
)}
{visualisationType === "grid" && (
  <GridChart
    cells={step.grid}
    rows={step.rows}
    cols={step.cols}
    currentCell={step.currentCell}
  />
)}
```

## 13.18 Performance notes

- **Tree layout**: `d3.tree()` is O(n) — very fast even for large trees. The bottleneck is SVG rendering. Keep trees under ~500 nodes for smooth interaction.
- **Grid layout**: No layout computation needed. The bottleneck is DOM elements. A 50×50 grid = 2,500 rects, which SVG handles fine. Beyond 100×100, consider Canvas.
- **Transitions**: Both components re-render on every step change. If animation stutters, reduce transition duration or skip transitions for rapid stepping.

## Summary

✅ You understand hierarchical data and `d3.hierarchy()`
✅ You can use `d3.tree()` to position nodes in a clean tree layout
✅ You know how to draw curved links between parent and child
✅ You can switch between vertical and horizontal tree orientations
✅ You built a grid layout for matrix-based visualisations
✅ You know how to colour cells by state and by value (heatmap)
✅ You can add dependency arrows to DP tables
✅ You understand when to use tree vs force vs grid layouts

## Key takeaways

**Tree layout** is deterministic — same data always produces the same visual. Use it whenever your data has a clear parent-child hierarchy. `d3.hierarchy()` + `d3.tree()` does the heavy lifting.

**Grid layout** doesn't need D3's layout algorithms at all — the position formula is trivial. D3's value is in data binding, transitions, and colour scales that make the grid come alive.

**Choose your layout based on the data structure**, not the algorithm name:
- Array → Bar chart
- Graph → Force layout
- Tree → Tree layout
- Matrix/2D array → Grid layout

---

→ [Back to Chapter 12: Polish and Deploy](./12-POLISH-AND-DEPLOY.md)
