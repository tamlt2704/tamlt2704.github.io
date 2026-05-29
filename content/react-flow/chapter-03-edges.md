# React Flow: Edges

[prev: Nodes](./chapter-02-nodes.md) | [next: Interaction](./chapter-04-interaction.md)

## Built-in Edge Types

- **default** (bezier) — Smooth curved line
- **straight** — Direct line between nodes
- **step** — Right-angle connections
- **smoothstep** — Rounded right-angle connections

```tsx
import { ReactFlow, Background } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "A" } },
  { id: "2", position: { x: 250, y: 0 }, data: { label: "B" } },
  { id: "3", position: { x: 0, y: 150 }, data: { label: "C" } },
  { id: "4", position: { x: 250, y: 150 }, data: { label: "D" } },
  { id: "5", position: { x: 0, y: 300 }, data: { label: "E" } },
  { id: "6", position: { x: 250, y: 300 }, data: { label: "F" } },
  { id: "7", position: { x: 0, y: 450 }, data: { label: "G" } },
  { id: "8", position: { x: 250, y: 450 }, data: { label: "H" } },
];

const edges: Edge[] = [
  { id: "e1", source: "1", target: "2", type: "default", label: "bezier" },
  { id: "e2", source: "3", target: "4", type: "straight", label: "straight" },
  { id: "e3", source: "5", target: "6", type: "step", label: "step" },
  { id: "e4", source: "7", target: "8", type: "smoothstep", label: "smoothstep" },
];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Animated Edges

```tsx
import { ReactFlow, Background } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Source" }, type: "input" },
  { id: "2", position: { x: 200, y: 150 }, data: { label: "Target" }, type: "output" },
];

const edges: Edge[] = [{ id: "e1-2", source: "1", target: "2", animated: true, label: "animated" }];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Edge Styles and Markers

```tsx
import { ReactFlow, Background, MarkerType } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Start" } },
  { id: "2", position: { x: 250, y: 0 }, data: { label: "End" } },
  { id: "3", position: { x: 0, y: 150 }, data: { label: "A" } },
  { id: "4", position: { x: 250, y: 150 }, data: { label: "B" } },
];

const edges: Edge[] = [
  {
    id: "e1-2",
    source: "1",
    target: "2",
    style: { stroke: "#ef4444", strokeWidth: 3 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#ef4444" },
    label: "red arrow",
  },
  {
    id: "e3-4",
    source: "3",
    target: "4",
    style: { stroke: "#3b82f6", strokeWidth: 2, strokeDasharray: "5 5" },
    markerEnd: { type: MarkerType.Arrow, color: "#3b82f6" },
    label: "dashed blue",
  },
];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Custom Edges

```tsx
import {
  ReactFlow,
  Background,
  BaseEdge,
  getSmoothStepPath,
  EdgeLabelRenderer,
} from "@xyflow/react";
import type { Node, Edge, EdgeProps, EdgeTypes } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function ButtonEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style,
  markerEnd,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });
  return (
    <>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} />
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: "all",
          }}
          className="nodrag nopan"
        >
          <button
            className="rounded bg-red-500 px-2 py-1 text-xs text-white"
            onClick={() => alert(`Delete ${id}`)}
          >
            x
          </button>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

const edgeTypes: EdgeTypes = { button: ButtonEdge };

const nodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Node A" } },
  { id: "2", position: { x: 300, y: 150 }, data: { label: "Node B" } },
];

const edges: Edge[] = [{ id: "e1-2", source: "1", target: "2", type: "button" }];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={edges} edgeTypes={edgeTypes} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Connection Line

Customize the line shown while dragging a new connection:

```tsx
import { ReactFlow, Background, ConnectionLineType } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes: Node[] = [
  { id: "1", type: "input", position: { x: 0, y: 0 }, data: { label: "Drag from here" } },
  { id: "2", type: "output", position: { x: 300, y: 150 }, data: { label: "To here" } },
];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={[]}
        connectionLineType={ConnectionLineType.SmoothStep}
        connectionLineStyle={{ stroke: "#6366f1", strokeWidth: 2 }}
        fitView
      >
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Self-Connecting Edges

Nodes can connect to themselves:

```tsx
import { ReactFlow, Handle, Position, Background } from "@xyflow/react";
import type { Node, Edge, NodeProps, NodeTypes } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function SelfNode({ data }: NodeProps) {
  return (
    <div className="rounded-lg border-2 border-purple-500 bg-white px-4 py-2">
      <Handle type="target" position={Position.Left} />
      <span>{data.label}</span>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes: NodeTypes = { self: SelfNode };

const nodes: Node[] = [
  { id: "1", type: "self", position: { x: 100, y: 100 }, data: { label: "Loop Node" } },
];

const edges: Edge[] = [
  {
    id: "e1-1",
    source: "1",
    target: "1",
    type: "smoothstep",
    style: { stroke: "#8b5cf6" },
    label: "self-loop",
  },
];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```
