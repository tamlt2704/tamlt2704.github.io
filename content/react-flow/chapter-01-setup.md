# React Flow: Setup

[prev: Overview](./chapter-00-overview.md) | [next: Nodes](./chapter-02-nodes.md)

## Installation

```tsx
// npm install @xyflow/react
// The package includes TypeScript types out of the box
```

## Basic ReactFlow Component

```tsx
import { ReactFlow, Background, Controls, MiniMap } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initialNodes: Node[] = [
  { id: "1", type: "input", position: { x: 250, y: 0 }, data: { label: "Input Node" } },
  { id: "2", position: { x: 100, y: 100 }, data: { label: "Default Node" } },
  { id: "3", type: "output", position: { x: 250, y: 200 }, data: { label: "Output Node" } },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" },
];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
```

## ReactFlowProvider

Wrap your app with `ReactFlowProvider` when you need to access React Flow state from components outside the `ReactFlow` component:

```tsx
import { ReactFlow, ReactFlowProvider, useReactFlow } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes: Node[] = [{ id: "1", position: { x: 0, y: 0 }, data: { label: "Hello" } }];
const edges: Edge[] = [];

function Toolbar() {
  const { fitView, zoomIn, zoomOut } = useReactFlow();
  return (
    <div className="absolute top-4 left-4 z-10 flex gap-2">
      <button onClick={() => zoomIn()} className="rounded bg-white px-3 py-1 shadow">
        +
      </button>
      <button onClick={() => zoomOut()} className="rounded bg-white px-3 py-1 shadow">
        -
      </button>
      <button onClick={() => fitView()} className="rounded bg-white px-3 py-1 shadow">
        Fit
      </button>
    </div>
  );
}

function Flow() {
  return (
    <div className="relative h-screen w-screen">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Toolbar />
      </ReactFlow>
    </div>
  );
}

export default function App() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}
```

## TypeScript Types

```tsx
import type {
  Node,
  Edge,
  NodeTypes,
  EdgeTypes,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  Connection,
  NodeProps,
  EdgeProps,
  Position,
  XYPosition,
} from "@xyflow/react";

// Custom node data typing
type MyNodeData = { label: string; value: number };

const myNode: Node<MyNodeData> = {
  id: "1",
  type: "custom",
  position: { x: 0, y: 0 },
  data: { label: "Typed", value: 42 },
};
```

## fitView Options

```tsx
import { ReactFlow } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "A" } },
  { id: "2", position: { x: 300, y: 200 }, data: { label: "B" } },
];
const edges: Edge[] = [{ id: "e1-2", source: "1", target: "2" }];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.2, maxZoom: 1.5 }}
      />
    </div>
  );
}
```

## Default Styles

Always import the default stylesheet — without it, nodes and edges won't render correctly:

```tsx
import "@xyflow/react/dist/style.css";
```

You can override styles with CSS or Tailwind by targeting `.react-flow` class selectors.
