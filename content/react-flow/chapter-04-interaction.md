# React Flow: Interaction

[prev: Edges](./chapter-03-edges.md) | [next: Advanced Custom Nodes](./chapter-05-custom-nodes.md)

## onNodesChange, onEdgesChange, onConnect

These are the core callbacks for making the flow interactive:

```tsx
import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
} from "@xyflow/react";
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from "@xyflow/react";
import { useState } from "react";
import "@xyflow/react/dist/style.css";

const initNodes: Node[] = [
  { id: "1", type: "input", position: { x: 0, y: 0 }, data: { label: "Start" } },
  { id: "2", position: { x: 200, y: 100 }, data: { label: "Middle" } },
  { id: "3", type: "output", position: { x: 400, y: 200 }, data: { label: "End" } },
];

const initEdges: Edge[] = [{ id: "e1-2", source: "1", target: "2" }];

export default function App() {
  const [nodes, setNodes] = useState(initNodes);
  const [edges, setEdges] = useState(initEdges);

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [],
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [],
  );
  const onConnect: OnConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    [],
  );

  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

## Drag and Drop from Sidebar

```tsx
import { useCallback, useState, DragEvent } from "react";
import {
  ReactFlow,
  Background,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  useReactFlow,
  ReactFlowProvider,
} from "@xyflow/react";
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

let id = 0;
const getId = () => `dnd_${id++}`;

function Sidebar() {
  const onDragStart = (event: DragEvent, nodeType: string) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };
  return (
    <aside className="w-48 border-r bg-gray-50 p-4">
      <p className="mb-2 text-sm font-bold">Drag nodes</p>
      <div
        className="mb-2 cursor-grab rounded bg-blue-100 p-2"
        onDragStart={(e) => onDragStart(e, "default")}
        draggable
      >
        Default Node
      </div>
      <div
        className="cursor-grab rounded bg-green-100 p-2"
        onDragStart={(e) => onDragStart(e, "output")}
        draggable
      >
        Output Node
      </div>
    </aside>
  );
}

function Flow() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const { screenToFlowPosition } = useReactFlow();

  const onNodesChange: OnNodesChange = useCallback(
    (c) => setNodes((n) => applyNodeChanges(c, n)),
    [],
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (c) => setEdges((e) => applyEdgeChanges(c, e)),
    [],
  );
  const onConnect: OnConnect = useCallback((c) => setEdges((e) => addEdge(c, e)), []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData("application/reactflow");
      if (!type) return;
      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      setNodes((nds) => [...nds, { id: getId(), type, position, data: { label: type } }]);
    },
    [screenToFlowPosition],
  );

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  return (
    <div className="h-full flex-1">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        fitView
      >
        <Background />
      </ReactFlow>
    </div>
  );
}

export default function App() {
  return (
    <ReactFlowProvider>
      <div className="flex h-screen w-screen">
        <Sidebar />
        <Flow />
      </div>
    </ReactFlowProvider>
  );
}
```

## Delete and Selection

Nodes and edges can be deleted with Backspace/Delete when selected. Multi-select with Shift+click or drag selection box:

```tsx
import { useCallback, useState } from "react";
import { ReactFlow, Background, applyNodeChanges, applyEdgeChanges, addEdge } from "@xyflow/react";
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initNodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Select me" } },
  { id: "2", position: { x: 200, y: 0 }, data: { label: "Or me" } },
  { id: "3", position: { x: 100, y: 150 }, data: { label: "Delete with Backspace" } },
];
const initEdges: Edge[] = [
  { id: "e1-3", source: "1", target: "3" },
  { id: "e2-3", source: "2", target: "3" },
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
  const onConnect: OnConnect = useCallback((c) => setEdges((e) => addEdge(c, e)), []);

  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        deleteKeyCode="Backspace"
        multiSelectionKeyCode="Shift"
        selectionOnDrag
        fitView
      >
        <Background />
      </ReactFlow>
    </div>
  );
}
```

## Undo/Redo Pattern

```tsx
import { useCallback, useState, useRef } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
} from "@xyflow/react";
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type Snapshot = { nodes: Node[]; edges: Edge[] };

const initNodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Move me" } },
  { id: "2", position: { x: 200, y: 100 }, data: { label: "Then undo" } },
];
const initEdges: Edge[] = [{ id: "e1-2", source: "1", target: "2" }];

export default function App() {
  const [nodes, setNodes] = useState(initNodes);
  const [edges, setEdges] = useState(initEdges);
  const history = useRef<Snapshot[]>([{ nodes: initNodes, edges: initEdges }]);
  const pointer = useRef(0);

  const takeSnapshot = () => {
    pointer.current++;
    history.current = history.current.slice(0, pointer.current);
    history.current.push({ nodes, edges });
  };

  const undo = () => {
    if (pointer.current > 0) {
      pointer.current--;
      const snap = history.current[pointer.current];
      setNodes(snap.nodes);
      setEdges(snap.edges);
    }
  };

  const redo = () => {
    if (pointer.current < history.current.length - 1) {
      pointer.current++;
      const snap = history.current[pointer.current];
      setNodes(snap.nodes);
      setEdges(snap.edges);
    }
  };

  const onNodesChange: OnNodesChange = useCallback(
    (c) => setNodes((n) => applyNodeChanges(c, n)),
    [],
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (c) => setEdges((e) => applyEdgeChanges(c, e)),
    [],
  );
  const onConnect: OnConnect = useCallback(
    (c) => {
      setEdges((e) => addEdge(c, e));
      takeSnapshot();
    },
    [nodes, edges],
  );

  return (
    <div className="relative h-screen w-screen">
      <div className="absolute top-4 left-4 z-10 flex gap-2">
        <button onClick={undo} className="rounded bg-white px-3 py-1 shadow">
          Undo
        </button>
        <button onClick={redo} className="rounded bg-white px-3 py-1 shadow">
          Redo
        </button>
        <button onClick={takeSnapshot} className="rounded bg-blue-500 px-3 py-1 text-white shadow">
          Save
        </button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

## Context Menu (Right-Click)

```tsx
import { useCallback, useState } from "react";
import { ReactFlow, Background, applyNodeChanges, applyEdgeChanges } from "@xyflow/react";
import type { Node, Edge, OnNodesChange, OnEdgesChange, NodeMouseHandler } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initNodes: Node[] = [
  { id: "1", position: { x: 100, y: 50 }, data: { label: "Right-click me" } },
  { id: "2", position: { x: 100, y: 200 }, data: { label: "Or me" } },
];

export default function App() {
  const [nodes, setNodes] = useState(initNodes);
  const [edges, setEdges] = useState<Edge[]>([{ id: "e1-2", source: "1", target: "2" }]);
  const [menu, setMenu] = useState<{ x: number; y: number; nodeId: string } | null>(null);

  const onNodesChange: OnNodesChange = useCallback(
    (c) => setNodes((n) => applyNodeChanges(c, n)),
    [],
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (c) => setEdges((e) => applyEdgeChanges(c, e)),
    [],
  );

  const onNodeContextMenu: NodeMouseHandler = useCallback((event, node) => {
    event.preventDefault();
    setMenu({ x: event.clientX, y: event.clientY, nodeId: node.id });
  }, []);

  const deleteNode = () => {
    if (menu) {
      setNodes((nds) => nds.filter((n) => n.id !== menu.nodeId));
      setEdges((eds) => eds.filter((e) => e.source !== menu.nodeId && e.target !== menu.nodeId));
      setMenu(null);
    }
  };

  return (
    <div className="h-screen w-screen" onClick={() => setMenu(null)}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeContextMenu={onNodeContextMenu}
        onPaneClick={() => setMenu(null)}
        fitView
      >
        <Background />
      </ReactFlow>
      {menu && (
        <div
          className="fixed z-50 rounded border bg-white p-2 shadow-lg"
          style={{ left: menu.x, top: menu.y }}
        >
          <button
            onClick={deleteNode}
            className="block w-full px-3 py-1 text-left text-red-600 hover:bg-red-50"
          >
            Delete Node
          </button>
        </div>
      )}
    </div>
  );
}
```

## Keyboard Shortcuts

React Flow supports these built-in shortcuts:

- **Backspace / Delete** — Remove selected nodes/edges
- **Ctrl+A** — Select all
- **Escape** — Deselect all
- **Shift+Click** — Multi-select

Custom shortcuts can be added via `onKeyDown` on the wrapper div or with a `useEffect` listener.
