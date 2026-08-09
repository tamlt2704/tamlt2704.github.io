# Chapter 10: Graph Visualisation — BFS and DFS

## What you'll learn

- How to represent a graph in code
- How D3's force layout positions nodes automatically
- How to visualise BFS (breadth-first) and DFS (depth-first) traversals
- A new step type for graph algorithms

## 10.1 A different kind of visualisation

Sorting algorithms work on arrays → bars. Graph algorithms work on nodes and edges → circles and lines. We need a new visualisation component.

The challenge with graphs: **positioning**. An array has a natural left-to-right order. A graph doesn't — you need an algorithm just to decide WHERE to draw each node.

D3's **force simulation** solves this. It treats nodes as charged particles that repel each other, with edges acting as springs. After a few iterations, it settles into a readable layout.

> **Why force layout?** Because it works for any graph shape — trees, cycles, disconnected components — without manual positioning. You don't need to know the graph structure in advance.
>
> **Alternatives:**
> - Manual positioning (works for small, known graphs — not scalable)
> - Tree layout (`d3.tree()`) — only for hierarchical/tree structures
> - Grid layout — only for lattice-like structures
>
> Force layout is the general-purpose solution.

## 10.2 Define graph types

Add to `app/algorithms/lib/types.ts`:

```ts
export type GraphNode = {
  id: string;
  label: string;
};

export type GraphEdge = {
  source: string;
  target: string;
};

export type GraphStep = {
  codeLine: number;
  description: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  visitedNodes: string[];      // already processed (grey)
  currentNode: string | null;  // currently being processed (red)
  queueOrStack: string[];      // nodes waiting to be processed (yellow)
  discoveredEdge: [string, string] | null; // edge being traversed (highlighted)
};
```

## 10.3 Build the GraphChart component

Create `app/algorithms/components/GraphChart.tsx`:

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

type GraphChartProps = {
  nodes: { id: string; label: string }[];
  edges: { source: string; target: string }[];
  visitedNodes?: string[];
  currentNode?: string | null;
  queueOrStack?: string[];
  discoveredEdge?: [string, string] | null;
  width?: number;
  height?: number;
};

type SimNode = d3.SimulationNodeDatum & { id: string; label: string };
type SimLink = d3.SimulationLinkDatum<SimNode> & { source: string | SimNode; target: string | SimNode };

export default function GraphChart({
  nodes,
  edges,
  visitedNodes = [],
  currentNode = null,
  queueOrStack = [],
  discoveredEdge = null,
  width = 500,
  height = 400,
}: GraphChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<SimNode, SimLink> | null>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Create simulation nodes and links
    const simNodes: SimNode[] = nodes.map((n) => ({ ...n }));
    const simLinks: SimLink[] = edges.map((e) => ({ ...e }));

    // Force simulation
    const simulation = d3
      .forceSimulation<SimNode>(simNodes)
      .force("link", d3.forceLink<SimNode, SimLink>(simLinks).id((d) => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide(30));

    simulationRef.current = simulation;

    // Draw edges
    const link = svg
      .append("g")
      .selectAll("line")
      .data(simLinks)
      .enter()
      .append("line")
      .attr("stroke", (d) => {
        const src = typeof d.source === "string" ? d.source : d.source.id;
        const tgt = typeof d.target === "string" ? d.target : d.target.id;
        if (discoveredEdge && src === discoveredEdge[0] && tgt === discoveredEdge[1]) {
          return "#ef4444"; // red for active edge
        }
        return "#cbd5e1";
      })
      .attr("stroke-width", (d) => {
        const src = typeof d.source === "string" ? d.source : d.source.id;
        const tgt = typeof d.target === "string" ? d.target : d.target.id;
        if (discoveredEdge && src === discoveredEdge[0] && tgt === discoveredEdge[1]) {
          return 3;
        }
        return 1.5;
      });

    // Draw nodes
    const node = svg
      .append("g")
      .selectAll<SVGGElement, SimNode>("g")
      .data(simNodes)
      .enter()
      .append("g");

    node
      .append("circle")
      .attr("r", 20)
      .attr("fill", (d) => {
        if (d.id === currentNode) return "#ef4444";  // red = currently processing
        if (queueOrStack.includes(d.id)) return "#fbbf24"; // yellow = in queue/stack
        if (visitedNodes.includes(d.id)) return "#9ca3af";  // grey = done
        return "#3b82f6"; // blue = undiscovered
      })
      .attr("stroke", "#1e293b")
      .attr("stroke-width", 2);

    node
      .append("text")
      .text((d) => d.label)
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .attr("fill", "white");

    // Update positions on each simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as SimNode).x || 0)
        .attr("y1", (d) => (d.source as SimNode).y || 0)
        .attr("x2", (d) => (d.target as SimNode).x || 0)
        .attr("y2", (d) => (d.target as SimNode).y || 0);

      node.attr("transform", (d) => `translate(${d.x || 0},${d.y || 0})`);
    });

    // Let simulation settle quickly
    simulation.alpha(1).restart();

    return () => {
      simulation.stop();
    };
  }, [nodes, edges, visitedNodes, currentNode, queueOrStack, discoveredEdge, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}
```

## 10.4 Understanding the force simulation

```tsx
d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).distance(80))   // edges act as springs
  .force("charge", d3.forceManyBody().strength(-300)) // nodes repel each other
  .force("center", d3.forceCenter(width/2, height/2)) // pull toward center
  .force("collision", d3.forceCollide(30))            // prevent overlap
```

The simulation runs iteratively:
1. Calculate forces on each node
2. Move each node slightly based on forces
3. Repeat until settled (or stopped)

The `tick` event fires on each iteration, letting us update the SVG positions.

> **Why not compute positions once?** You could: run the simulation for 300 iterations, read final positions, draw once. We use the live simulation because it handles dynamic graphs (nodes being added/highlighted) and looks more alive. For a static teaching tool, pre-computed positions work fine too.

## 10.5 Generate BFS steps

Create `app/algorithms/lib/bfs.ts`:

```ts
import { GraphStep, GraphNode, GraphEdge } from "./types";

export const BFS_CODE_JAVA = [
  "public void bfs(Graph graph, String start) {",
  "  Queue<String> queue = new LinkedList<>();",
  "  Set<String> visited = new HashSet<>();",
  "  queue.add(start);",
  "  visited.add(start);",
  "  while (!queue.isEmpty()) {",
  "    String current = queue.poll();",
  "    process(current);",
  "    for (String neighbor : graph.neighbors(current)) {",
  "      if (!visited.contains(neighbor)) {",
  "        visited.add(neighbor);",
  "        queue.add(neighbor);",
  "      }",
  "    }",
  "  }",
  "}",
];

export function generateBfsSteps(
  nodes: GraphNode[],
  edges: GraphEdge[],
  startNode: string
): GraphStep[] {
  const steps: GraphStep[] = [];

  // Build adjacency list
  const adj: Record<string, string[]> = {};
  nodes.forEach((n) => (adj[n.id] = []));
  edges.forEach((e) => {
    adj[e.source].push(e.target);
    adj[e.target].push(e.source); // undirected
  });

  const visited = new Set<string>();
  const queue: string[] = [];

  // Initial state
  steps.push({
    codeLine: 0,
    description: "Start BFS — explore all nodes level by level",
    nodes,
    edges,
    visitedNodes: [],
    currentNode: null,
    queueOrStack: [],
    discoveredEdge: null,
  });

  // Add start to queue
  queue.push(startNode);
  visited.add(startNode);

  steps.push({
    codeLine: 3,
    description: `Add starting node "${startNode}" to the queue`,
    nodes,
    edges,
    visitedNodes: [],
    currentNode: null,
    queueOrStack: [...queue],
    discoveredEdge: null,
  });

  while (queue.length > 0) {
    const current = queue.shift()!;

    steps.push({
      codeLine: 6,
      description: `Dequeue "${current}" — process it`,
      nodes,
      edges,
      visitedNodes: [...visited].filter((n) => n !== current),
      currentNode: current,
      queueOrStack: [...queue],
      discoveredEdge: null,
    });

    // Explore neighbors
    for (const neighbor of adj[current]) {
      steps.push({
        codeLine: 8,
        description: `Check neighbor "${neighbor}" of "${current}"`,
        nodes,
        edges,
        visitedNodes: [...visited].filter((n) => n !== current),
        currentNode: current,
        queueOrStack: [...queue],
        discoveredEdge: [current, neighbor],
      });

      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push(neighbor);

        steps.push({
          codeLine: 11,
          description: `"${neighbor}" not visited — add to queue. Queue: [${queue.join(", ")}]`,
          nodes,
          edges,
          visitedNodes: [...visited].filter((n) => n !== current),
          currentNode: current,
          queueOrStack: [...queue],
          discoveredEdge: [current, neighbor],
        });
      } else {
        steps.push({
          codeLine: 9,
          description: `"${neighbor}" already visited — skip`,
          nodes,
          edges,
          visitedNodes: [...visited].filter((n) => n !== current),
          currentNode: current,
          queueOrStack: [...queue],
          discoveredEdge: null,
        });
      }
    }
  }

  steps.push({
    codeLine: 14,
    description: "BFS complete — all reachable nodes visited!",
    nodes,
    edges,
    visitedNodes: [...visited],
    currentNode: null,
    queueOrStack: [],
    discoveredEdge: null,
  });

  return steps;
}
```

## 10.6 The colour legend

For graph visualisation, colours carry specific meaning:

| Colour | Meaning |
|--------|---------|
| 🔵 Blue | Undiscovered — hasn't been seen yet |
| 🟡 Yellow | In queue/stack — discovered but not yet processed |
| 🔴 Red | Currently processing — the active node |
| ⚫ Grey | Visited — fully processed, all neighbors explored |

This mirrors how textbooks explain BFS/DFS. The visualisation makes the state transitions visible.

## 10.7 Integrating graphs into the page

You'll need a conditional render based on algorithm type — sorting algorithms show BarChart, graph algorithms show GraphChart. Create a wrapper:

```tsx
// In page.tsx
const isGraphAlgorithm = algorithm === "bfs" || algorithm === "dfs";

// In the VisualisationPanel:
{isGraphAlgorithm ? (
  <GraphChart
    nodes={step.nodes}
    edges={step.edges}
    visitedNodes={step.visitedNodes}
    currentNode={step.currentNode}
    queueOrStack={step.queueOrStack}
    discoveredEdge={step.discoveredEdge}
  />
) : (
  <RoughBarChart
    data={step.array}
    highlightIndices={[...step.comparing, ...step.sorted]}
  />
)}
```

You'll need a union type for steps — either an `AlgorithmStep` (arrays) or a `GraphStep` (graphs). Or a single type that covers both with optional fields.

## 10.8 DFS — a minimal change

DFS is almost identical to BFS — just replace the queue with a stack:

```ts
// BFS: queue.shift() — FIFO (first in, first out)
const current = queue.shift()!;

// DFS: stack.pop() — LIFO (last in, first out)
const current = stack.pop()!;
```

The visualisation is the same component, same colours, same step structure. Only the traversal order differs — which is exactly the point the visualiser teaches.

## Summary

✅ You built a force-directed graph layout  
✅ You defined `GraphStep` type for graph algorithm state  
✅ You implemented BFS step generation  
✅ You understand the colour coding (undiscovered → in queue → processing → visited)  
✅ You know how DFS differs from BFS (stack vs queue — one line change!)  

## Key takeaway

**D3's force simulation positions nodes automatically.** You define the forces (repulsion, spring links, centering), and the simulation finds a stable layout. This means your graph visualisation works for ANY graph shape — you don't need to manually position anything.

---

→ [Chapter 11: Multi-Language Support](./11-MULTI-LANGUAGE.md)
