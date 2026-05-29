# React Flow: Auto-Layout

[prev: Advanced Custom Nodes](./chapter-05-custom-nodes.md) | [next: State Management](./chapter-07-state.md)

## Dagre (Hierarchical Layout)

Dagre is the most popular layout library for directed graphs. Install with `npm install @dagrejs/dagre`.

```tsx
import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  Panel,
} from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import Dagre from "@dagrejs/dagre";
import "@xyflow/react/dist/style.css";

const initialNodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Start" } },
  { id: "2", position: { x: 0, y: 0 }, data: { label: "Step A" } },
  { id: "3", position: { x: 0, y: 0 }, data: { label: "Step B" } },
  { id: "4", position: { x: 0, y: 0 }, data: { label: "Step C" } },
  { id: "5", position: { x: 0, y: 0 }, data: { label: "End" } },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e1-3", source: "1", target: "3" },
  { id: "e2-4", source: "2", target: "4" },
  { id: "e3-4", source: "3", target: "4" },
  { id: "e4-5", source: "4", target: "5" },
];

function getLayoutedElements(nodes: Node[], edges: Edge[], direction = "TB") {
  const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: direction, nodesep: 50, ranksep: 80 });

  nodes.forEach((node) => g.setNode(node.id, { width: 150, height: 40 }));
  edges.forEach((edge) => g.setEdge(edge.source, edge.target));
  Dagre.layout(g);

  const layoutedNodes = nodes.map((node) => {
    const pos = g.node(node.id);
    return { ...node, position: { x: pos.x - 75, y: pos.y - 20 } };
  });
  return { nodes: layoutedNodes, edges };
}

export default function App() {
  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(
    () => getLayoutedElements(initialNodes, initialEdges, "TB"),
    [],
  );
  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  const onLayout = useCallback(
    (direction: string) => {
      const { nodes: ln, edges: le } = getLayoutedElements(nodes, edges, direction);
      setNodes(ln);
      setEdges(le);
    },
    [nodes, edges],
  );

  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Panel position="top-left">
          <div className="flex gap-2">
            <button
              onClick={() => onLayout("TB")}
              className="rounded bg-white px-3 py-1 text-sm shadow"
            >
              Top-Bottom
            </button>
            <button
              onClick={() => onLayout("LR")}
              className="rounded bg-white px-3 py-1 text-sm shadow"
            >
              Left-Right
            </button>
            <button
              onClick={() => onLayout("BT")}
              className="rounded bg-white px-3 py-1 text-sm shadow"
            >
              Bottom-Top
            </button>
            <button
              onClick={() => onLayout("RL")}
              className="rounded bg-white px-3 py-1 text-sm shadow"
            >
              Right-Left
            </button>
          </div>
        </Panel>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

## ELK (Advanced Layout)

ELK provides more sophisticated layout algorithms. Install with `npm install elkjs`.

```tsx
import { useCallback, useEffect, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
} from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import ELK from "elkjs/lib/elk.bundled.js";
import "@xyflow/react/dist/style.css";

const elk = new ELK();

const initialNodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Root" } },
  { id: "2", position: { x: 0, y: 0 }, data: { label: "Branch A" } },
  { id: "3", position: { x: 0, y: 0 }, data: { label: "Branch B" } },
  { id: "4", position: { x: 0, y: 0 }, data: { label: "Leaf 1" } },
  { id: "5", position: { x: 0, y: 0 }, data: { label: "Leaf 2" } },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e1-3", source: "1", target: "3" },
  { id: "e2-4", source: "2", target: "4" },
  { id: "e3-5", source: "3", target: "5" },
];

async function getLayoutedElements(nodes: Node[], edges: Edge[]) {
  const graph = {
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": "DOWN",
      "elk.spacing.nodeNode": "80",
    },
    children: nodes.map((n) => ({ id: n.id, width: 150, height: 40 })),
    edges: edges.map((e) => ({ id: e.id, sources: [e.source], targets: [e.target] })),
  };
  const layout = await elk.layout(graph);
  const layoutedNodes = nodes.map((node) => {
    const elkNode = layout.children?.find((n) => n.id === node.id);
    return { ...node, position: { x: elkNode?.x ?? 0, y: elkNode?.y ?? 0 } };
  });
  return { nodes: layoutedNodes, edges };
}

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    getLayoutedElements(initialNodes, initialEdges).then(({ nodes, edges }) => {
      setNodes(nodes);
      setEdges(edges);
    });
  }, []);

  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

## D3-Hierarchy (Tree Layout)

For tree structures, `d3-hierarchy` provides clean layouts. Install with `npm install d3-hierarchy`.

```tsx
import { ReactFlow, Background, Controls } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import { stratify, tree } from "d3-hierarchy";
import "@xyflow/react/dist/style.css";

const data = [
  { id: "1", parentId: null, label: "CEO" },
  { id: "2", parentId: "1", label: "CTO" },
  { id: "3", parentId: "1", label: "CFO" },
  { id: "4", parentId: "2", label: "Dev Lead" },
  { id: "5", parentId: "2", label: "QA Lead" },
  { id: "6", parentId: "3", label: "Accountant" },
];

function buildTree(): { nodes: Node[]; edges: Edge[] } {
  const root = stratify<(typeof data)[0]>()
    .id((d) => d.id)
    .parentId((d) => d.parentId)(data);

  const layout = tree<(typeof data)[0]>().nodeSize([180, 100])(root);

  const nodes: Node[] = layout.descendants().map((d) => ({
    id: d.data.id,
    position: { x: d.x, y: d.y },
    data: { label: d.data.label },
  }));

  const edges: Edge[] = layout.links().map((link) => ({
    id: `e${link.source.data.id}-${link.target.data.id}`,
    source: link.source.data.id,
    target: link.target.data.id,
  }));

  return { nodes, edges };
}

const { nodes, edges } = buildTree();

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

## Force-Directed Layout

Use `d3-force` for physics-based layouts. Install with `npm install d3-force`.

```tsx
import { useEffect, useState } from "react";
import { ReactFlow, Background } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from "d3-force";
import "@xyflow/react/dist/style.css";

const rawNodes = ["A", "B", "C", "D", "E", "F"].map((label, i) => ({
  id: String(i + 1),
  position: { x: 0, y: 0 },
  data: { label },
}));

const rawEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e1-3", source: "1", target: "3" },
  { id: "e2-4", source: "2", target: "4" },
  { id: "e3-5", source: "3", target: "5" },
  { id: "e4-6", source: "4", target: "6" },
  { id: "e5-6", source: "5", target: "6" },
];

function applyForceLayout(nodes: Node[], edges: Edge[]): Node[] {
  const simNodes = nodes.map((n) => ({ ...n, x: Math.random() * 400, y: Math.random() * 400 }));
  const simLinks = edges.map((e) => ({ source: e.source, target: e.target }));

  const sim = forceSimulation(simNodes as any)
    .force(
      "link",
      forceLink(simLinks as any)
        .id((d: any) => d.id)
        .distance(120),
    )
    .force("charge", forceManyBody().strength(-300))
    .force("center", forceCenter(200, 200))
    .force("collide", forceCollide(60))
    .stop();

  for (let i = 0; i < 300; i++) sim.tick();

  return simNodes.map((sn: any) => ({
    ...nodes.find((n) => n.id === sn.id)!,
    position: { x: sn.x, y: sn.y },
  }));
}

export default function App() {
  const [nodes, setNodes] = useState<Node[]>([]);

  useEffect(() => {
    setNodes(applyForceLayout(rawNodes, rawEdges));
  }, []);

  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={rawEdges} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Layout Direction Options

All layout libraries support direction configuration:

| Direction | Description             |
| --------- | ----------------------- |
| TB        | Top to Bottom (default) |
| BT        | Bottom to Top           |
| LR        | Left to Right           |
| RL        | Right to Left           |

Pass the direction to your layout algorithm's options (e.g., `rankdir` for dagre, `elk.direction` for ELK).
