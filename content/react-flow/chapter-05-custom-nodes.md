# React Flow: Advanced Custom Nodes

[prev: Interaction](./chapter-04-interaction.md) | [next: Auto-Layout](./chapter-06-layout.md)

## Forms Inside Nodes

```tsx
import { useCallback, useState } from "react";
import { ReactFlow, Handle, Position, Background, applyNodeChanges } from "@xyflow/react";
import type { Node, NodeProps, NodeTypes, OnNodesChange } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function FormNode({ data, id }: NodeProps) {
  const [value, setValue] = useState(data.label);
  return (
    <div className="min-w-[200px] rounded-lg border-2 border-blue-400 bg-white p-3">
      <Handle type="target" position={Position.Top} />
      <label className="mb-1 block text-xs text-gray-500">Name</label>
      <input
        className="nodrag w-full rounded border px-2 py-1 text-sm"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

const nodeTypes: NodeTypes = { form: FormNode };

const initNodes: Node[] = [
  { id: "1", type: "form", position: { x: 0, y: 0 }, data: { label: "Hello" } },
  { id: "2", type: "form", position: { x: 0, y: 150 }, data: { label: "World" } },
];

export default function App() {
  const [nodes, setNodes] = useState(initNodes);
  const onNodesChange: OnNodesChange = useCallback(
    (c) => setNodes((n) => applyNodeChanges(c, n)),
    [],
  );
  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={[{ id: "e1-2", source: "1", target: "2" }]}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        fitView
      >
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Dropdown and Color Picker Nodes

```tsx
import { useState, useCallback } from "react";
import { ReactFlow, Handle, Position, Background, applyNodeChanges } from "@xyflow/react";
import type { Node, NodeProps, NodeTypes, OnNodesChange } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function SelectNode({ data }: NodeProps) {
  const [selected, setSelected] = useState("option1");
  return (
    <div className="rounded-lg border-2 border-orange-400 bg-white p-3">
      <Handle type="target" position={Position.Top} />
      <p className="mb-1 text-xs font-bold">{data.label}</p>
      <select
        className="nodrag w-full rounded border px-2 py-1 text-sm"
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
      >
        <option value="option1">Option 1</option>
        <option value="option2">Option 2</option>
        <option value="option3">Option 3</option>
      </select>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

function ColorNode({ data }: NodeProps) {
  const [color, setColor] = useState("#6366f1");
  return (
    <div
      className="rounded-lg border-2 border-gray-300 bg-white p-3"
      style={{ borderColor: color }}
    >
      <Handle type="target" position={Position.Top} />
      <p className="mb-1 text-xs font-bold">{data.label}</p>
      <input
        type="color"
        value={color}
        onChange={(e) => setColor(e.target.value)}
        className="nodrag h-8 w-full cursor-pointer"
      />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

const nodeTypes: NodeTypes = { select: SelectNode, color: ColorNode };

const nodes: Node[] = [
  { id: "1", type: "select", position: { x: 0, y: 0 }, data: { label: "Dropdown" } },
  { id: "2", type: "color", position: { x: 250, y: 0 }, data: { label: "Color Picker" } },
];

export default function App() {
  const [nds, setNds] = useState(nodes);
  const onNodesChange: OnNodesChange = useCallback(
    (c) => setNds((n) => applyNodeChanges(c, n)),
    [],
  );
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nds} edges={[]} nodeTypes={nodeTypes} onNodesChange={onNodesChange} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Node Toolbar

```tsx
import { useState, useCallback } from "react";
import {
  ReactFlow,
  Handle,
  Position,
  Background,
  applyNodeChanges,
  NodeToolbar,
} from "@xyflow/react";
import type { Node, NodeProps, NodeTypes, OnNodesChange } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function ToolbarNode({ data, selected }: NodeProps) {
  return (
    <div className="rounded-lg border-2 border-emerald-500 bg-white px-4 py-2">
      <NodeToolbar isVisible={selected} position={Position.Top}>
        <div className="flex gap-1 rounded border bg-white p-1 shadow">
          <button className="rounded px-2 py-1 text-xs hover:bg-gray-100">Edit</button>
          <button className="rounded px-2 py-1 text-xs hover:bg-gray-100">Copy</button>
          <button className="rounded px-2 py-1 text-xs text-red-500 hover:bg-red-50">Delete</button>
        </div>
      </NodeToolbar>
      <Handle type="target" position={Position.Left} />
      <span className="text-sm">{data.label}</span>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes: NodeTypes = { toolbar: ToolbarNode };

const initNodes: Node[] = [
  {
    id: "1",
    type: "toolbar",
    position: { x: 100, y: 100 },
    data: { label: "Click to see toolbar" },
  },
];

export default function App() {
  const [nodes, setNodes] = useState(initNodes);
  const onNodesChange: OnNodesChange = useCallback(
    (c) => setNodes((n) => applyNodeChanges(c, n)),
    [],
  );
  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={[]}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        fitView
      >
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Collapsible Groups / Sub-Flows

```tsx
import { useState, useCallback } from "react";
import { ReactFlow, Background, applyNodeChanges, applyEdgeChanges } from "@xyflow/react";
import type { Node, Edge, OnNodesChange, OnEdgesChange } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initNodes: Node[] = [
  {
    id: "group1",
    type: "group",
    position: { x: 0, y: 0 },
    data: { label: "Group" },
    style: { width: 300, height: 200, backgroundColor: "rgba(99,102,241,0.1)", borderRadius: 8 },
  },
  {
    id: "a",
    position: { x: 20, y: 40 },
    data: { label: "Child A" },
    parentId: "group1",
    extent: "parent",
  },
  {
    id: "b",
    position: { x: 150, y: 100 },
    data: { label: "Child B" },
    parentId: "group1",
    extent: "parent",
  },
  { id: "c", position: { x: 400, y: 80 }, data: { label: "Outside" } },
];

const initEdges: Edge[] = [
  { id: "ea-b", source: "a", target: "b" },
  { id: "eb-c", source: "b", target: "c" },
];

export default function App() {
  const [nodes, setNodes] = useState(initNodes);
  const [edges, setEdges] = useState(initEdges);
  const onNodesChange: OnNodesChange = useCallback(
    (c) => setNodes((n) => applyNodeChanges(c, n)),
    [],
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (c) => setEdges((e) => applyEdgeChanges(c, e)),
    [],
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
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Validation Indicators and Conditional Handles

```tsx
import { useState, useCallback } from "react";
import { ReactFlow, Handle, Position, Background, applyNodeChanges } from "@xyflow/react";
import type { Node, NodeProps, NodeTypes, OnNodesChange } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function ValidatedNode({ data }: NodeProps) {
  const isValid = data.value && data.value.length > 0;
  return (
    <div
      className={`rounded-lg border-2 bg-white p-3 ${isValid ? "border-green-500" : "border-red-500"}`}
    >
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2">
        <span className={`h-3 w-3 rounded-full ${isValid ? "bg-green-500" : "bg-red-500"}`} />
        <span className="text-sm font-medium">{data.label}</span>
      </div>
      {isValid && <Handle type="source" position={Position.Bottom} />}
    </div>
  );
}

const nodeTypes: NodeTypes = { validated: ValidatedNode };

const nodes: Node[] = [
  { id: "1", type: "validated", position: { x: 0, y: 0 }, data: { label: "Valid", value: "ok" } },
  { id: "2", type: "validated", position: { x: 200, y: 0 }, data: { label: "Invalid", value: "" } },
];

export default function App() {
  const [nds, setNds] = useState(nodes);
  const onNodesChange: OnNodesChange = useCallback(
    (c) => setNds((n) => applyNodeChanges(c, n)),
    [],
  );
  return (
    <div className="h-screen w-screen">
      <ReactFlow nodes={nds} edges={[]} nodeTypes={nodeTypes} onNodesChange={onNodesChange} fitView>
        <Background />
      </ReactFlow>
    </div>
  );
}
```
