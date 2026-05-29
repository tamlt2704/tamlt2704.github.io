# React Flow: Nodes

[prev: Setup](./chapter-01-setup.md) | [next: Edges](./chapter-03-edges.md)

## Built-in Node Types

React Flow provides three built-in node types:

- **default** — Has both source and target handles
- **input** — Only has a source handle (starting node)
- **output** — Only has a target handle (ending node)

```tsx
import { ReactFlow, Background } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes: Node[] = [
  { id: "1", type: "input", position: { x: 150, y: 0 }, data: { label: "Input" } },
  { id: "2", type: "default", position: { x: 0, y: 100 }, data: { label: "Default" } },
  { id: "3", type: "default", position: { x: 300, y: 100 }, data: { label: "Default 2" } },
  { id: "4", type: "output", position: { x: 150, y: 200 }, data: { label: "Output" } },
];

const edges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e1-3", source: "1", target: "3" },
  { id: "e2-4", source: "2", target: "4" },
  { id: "e3-4", source: "3", target: "4" },
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

## Custom Nodes

Define custom nodes as React components and register them via `nodeTypes`:

```tsx
import { ReactFlow, Handle, Position, Background } from "@xyflow/react";
import type { Node, Edge, NodeProps, NodeTypes } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type CustomData = { label: string; emoji: string };

function EmojiNode({ data }: NodeProps<Node<CustomData>>) {
  return (
    <div className="rounded-lg border-2 border-indigo-500 bg-white px-4 py-2 shadow-md">
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2">
        <span className="text-2xl">{data.emoji}</span>
        <span className="text-sm font-semibold">{data.label}</span>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

const nodeTypes: NodeTypes = { emoji: EmojiNode };

const nodes: Node[] = [
  { id: "1", type: "emoji", position: { x: 0, y: 0 }, data: { label: "Start", emoji: "🚀" } },
  { id: "2", type: "emoji", position: { x: 0, y: 120 }, data: { label: "Process", emoji: "⚙️" } },
  { id: "3", type: "emoji", position: { x: 0, y: 240 }, data: { label: "Done", emoji: "✅" } },
];

const edges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" },
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

## Handle Positions

Handles can be placed at `Top`, `Bottom`, `Left`, or `Right`:

```tsx
import { ReactFlow, Handle, Position, Background } from "@xyflow/react";
import type { Node, Edge, NodeProps, NodeTypes } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function MultiHandleNode({ data }: NodeProps) {
  return (
    <div className="rounded-lg border-2 border-gray-300 bg-white px-6 py-4">
      <Handle type="target" position={Position.Left} id="left" />
      <Handle type="target" position={Position.Top} id="top" />
      <span className="font-medium">{data.label}</span>
      <Handle type="source" position={Position.Right} id="right" />
      <Handle type="source" position={Position.Bottom} id="bottom" />
    </div>
  );
}

const nodeTypes: NodeTypes = { multi: MultiHandleNode };

const nodes: Node[] = [
  { id: "1", type: "input", position: { x: 0, y: 100 }, data: { label: "Left Source" } },
  { id: "2", type: "multi", position: { x: 250, y: 80 }, data: { label: "Multi Handle" } },
  { id: "3", type: "output", position: { x: 500, y: 100 }, data: { label: "Right Target" } },
];

const edges: Edge[] = [
  { id: "e1-2", source: "1", target: "2", targetHandle: "left" },
  { id: "e2-3", source: "2", target: "3", sourceHandle: "right" },
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

## Dynamic Handles

Generate handles based on data:

```tsx
import { ReactFlow, Handle, Position, Background } from "@xyflow/react";
import type { Node, NodeProps, NodeTypes } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type PortData = { label: string; inputs: string[]; outputs: string[] };

function DynamicPortNode({ data }: NodeProps<Node<PortData>>) {
  return (
    <div className="min-w-[150px] rounded-lg border-2 border-blue-500 bg-white p-3">
      <div className="mb-2 text-center text-sm font-bold">{data.label}</div>
      {data.inputs.map((_, i) => (
        <Handle
          key={`in-${i}`}
          type="target"
          position={Position.Left}
          id={`in-${i}`}
          style={{ top: 40 + i * 20 }}
        />
      ))}
      {data.outputs.map((_, i) => (
        <Handle
          key={`out-${i}`}
          type="source"
          position={Position.Right}
          id={`out-${i}`}
          style={{ top: 40 + i * 20 }}
        />
      ))}
    </div>
  );
}

const nodeTypes: NodeTypes = { dynamic: DynamicPortNode };

const nodes: Node[] = [
  {
    id: "1",
    type: "dynamic",
    position: { x: 0, y: 0 },
    data: { label: "Transform", inputs: ["a", "b"], outputs: ["x", "y", "z"] },
  },
];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={[]} nodeTypes={nodeTypes} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Node Resizing

Use the `NodeResizer` component:

```tsx
import { ReactFlow, Handle, Position, Background, NodeResizer } from "@xyflow/react";
import type { Node, NodeProps, NodeTypes } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function ResizableNode({ data, selected }: NodeProps) {
  return (
    <>
      <NodeResizer isVisible={selected} minWidth={100} minHeight={50} />
      <Handle type="target" position={Position.Top} />
      <div className="flex h-full w-full items-center justify-center p-2">
        <span className="text-sm">{data.label}</span>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </>
  );
}

const nodeTypes: NodeTypes = { resizable: ResizableNode };

const nodes: Node[] = [
  {
    id: "1",
    type: "resizable",
    position: { x: 100, y: 100 },
    data: { label: "Drag corners to resize" },
    style: { width: 200, height: 80 },
  },
];

export default function App() {
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nodes} edges={[]} nodeTypes={nodeTypes} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```
