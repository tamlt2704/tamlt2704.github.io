# React Flow: Overview

[next: Setup](./chapter-01-setup.md)

React Flow is a highly customizable library for building node-based editors, interactive diagrams, and workflow visualizations in React. It provides a canvas where users can create, connect, and manipulate nodes — making it ideal for visual programming interfaces.

## Why React Flow?

- Fully customizable nodes and edges with React components
- Built-in zoom, pan, and minimap
- TypeScript-first with excellent DX
- Performant with thousands of nodes
- Active community and ecosystem

## Use Cases

- **Workflow Builders** — Visual automation tools like n8n, Zapier, or Node-RED
- **Mind Maps** — Hierarchical idea organization with expandable branches
- **Data Pipelines** — DAG-based ETL/data processing visualizations
- **State Machines** — Visual state/transition editors (XState-style)
- **Org Charts** — Company hierarchy with expand/collapse

## Chapters

1. [Setup](./chapter-01-setup.md) — Installation, basic component, TypeScript types
2. [Nodes](./chapter-02-nodes.md) — Node types, custom nodes, handles, positioning
3. [Edges](./chapter-03-edges.md) — Edge types, custom edges, labels, markers
4. [Interaction](./chapter-04-interaction.md) — Events, drag-and-drop, keyboard shortcuts
5. [Advanced Custom Nodes](./chapter-05-custom-nodes.md) — Forms, toolbars, sub-flows
6. [Auto-Layout](./chapter-06-layout.md) — Dagre, ELK, force-directed algorithms
7. [State Management](./chapter-07-state.md) — Zustand, persistence, undo/redo
8. [Projects](./chapter-08-projects.md) — Full project examples

## Quick Example

```tsx
import { ReactFlow, Background, Controls } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Start" }, type: "input" },
  { id: "2", position: { x: 200, y: 100 }, data: { label: "Process" } },
  { id: "3", position: { x: 400, y: 0 }, data: { label: "End" }, type: "output" },
];

const edges = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" },
];

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
