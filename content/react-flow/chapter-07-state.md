# React Flow: State Management

[prev: Auto-Layout](./chapter-06-layout.md) | [next: Projects](./chapter-08-projects.md)

## useNodesState / useEdgesState Hooks

The simplest way to manage interactive state:

```tsx
import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  addEdge,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import type { OnConnect } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initNodes = [
  { id: "1", type: "input" as const, position: { x: 0, y: 0 }, data: { label: "A" } },
  { id: "2", position: { x: 200, y: 100 }, data: { label: "B" } },
  { id: "3", type: "output" as const, position: { x: 100, y: 200 }, data: { label: "C" } },
];

const initEdges = [{ id: "e1-2", source: "1", target: "2" }];

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initEdges);
  const onConnect: OnConnect = useCallback((c) => setEdges((eds) => addEdge(c, eds)), []);

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

## Zustand Integration

For complex apps, use Zustand to manage flow state globally. Install with `npm install zustand`.

```tsx
import { useCallback } from "react";
import { ReactFlow, Background, Controls, addEdge } from "@xyflow/react";
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from "@xyflow/react";
import { applyNodeChanges, applyEdgeChanges } from "@xyflow/react";
import { create } from "zustand";
import "@xyflow/react/dist/style.css";

type FlowState = {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  addNode: (node: Node) => void;
};

const useFlowStore = create<FlowState>((set, get) => ({
  nodes: [
    { id: "1", position: { x: 0, y: 0 }, data: { label: "Zustand Node 1" } },
    { id: "2", position: { x: 200, y: 100 }, data: { label: "Zustand Node 2" } },
  ],
  edges: [{ id: "e1-2", source: "1", target: "2" }],
  onNodesChange: (changes) => set({ nodes: applyNodeChanges(changes, get().nodes) }),
  onEdgesChange: (changes) => set({ edges: applyEdgeChanges(changes, get().edges) }),
  onConnect: (connection) => set({ edges: addEdge(connection, get().edges) }),
  addNode: (node) => set({ nodes: [...get().nodes, node] }),
}));

export default function App() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, addNode } = useFlowStore();

  const handleAdd = () => {
    const id = String(nodes.length + 1);
    addNode({
      id,
      position: { x: Math.random() * 300, y: Math.random() * 300 },
      data: { label: `Node ${id}` },
    });
  };

  return (
    <div className="relative h-screen w-screen">
      <button
        onClick={handleAdd}
        className="absolute top-4 left-4 z-10 rounded bg-indigo-500 px-3 py-1 text-white shadow"
      >
        Add Node
      </button>
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

## Persisting to Backend (Save/Load)

```tsx
import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
  useReactFlow,
  ReactFlowProvider,
} from "@xyflow/react";
import type { OnConnect } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const STORAGE_KEY = "react-flow-state";

const defaultNodes = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Save me" } },
  { id: "2", position: { x: 200, y: 100 }, data: { label: "Load me" } },
];
const defaultEdges = [{ id: "e1-2", source: "1", target: "2" }];

function Flow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultEdges);
  const onConnect: OnConnect = useCallback((c) => setEdges((e) => addEdge(c, e)), []);
  const { toObject } = useReactFlow();

  const save = () => {
    const flow = toObject();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(flow));
    alert("Saved!");
  };

  const load = () => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return alert("Nothing saved");
    const flow = JSON.parse(raw);
    setNodes(flow.nodes || []);
    setEdges(flow.edges || []);
  };

  return (
    <div className="relative h-screen w-screen">
      <div className="absolute top-4 left-4 z-10 flex gap-2">
        <button onClick={save} className="rounded bg-green-500 px-3 py-1 text-white shadow">
          Save
        </button>
        <button onClick={load} className="rounded bg-blue-500 px-3 py-1 text-white shadow">
          Load
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

export default function App() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}
```

## History (Undo/Redo with Immer)

Install with `npm install immer zustand`.

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
import { create } from "zustand";
import { produce } from "immer";
import "@xyflow/react/dist/style.css";

type State = { nodes: Node[]; edges: Edge[] };
type HistoryStore = {
  past: State[];
  present: State;
  future: State[];
  set: (fn: (state: State) => State) => void;
  undo: () => void;
  redo: () => void;
};

const initial: State = {
  nodes: [
    { id: "1", position: { x: 0, y: 0 }, data: { label: "Move me" } },
    { id: "2", position: { x: 200, y: 100 }, data: { label: "Then undo" } },
  ],
  edges: [{ id: "e1-2", source: "1", target: "2" }],
};

const useHistory = create<HistoryStore>((set) => ({
  past: [],
  present: initial,
  future: [],
  set: (fn) =>
    set(
      produce((draft: HistoryStore) => {
        draft.past.push(draft.present);
        draft.present = fn(draft.present);
        draft.future = [];
      }),
    ),
  undo: () =>
    set(
      produce((draft: HistoryStore) => {
        if (draft.past.length === 0) return;
        draft.future.unshift(draft.present);
        draft.present = draft.past.pop()!;
      }),
    ),
  redo: () =>
    set(
      produce((draft: HistoryStore) => {
        if (draft.future.length === 0) return;
        draft.past.push(draft.present);
        draft.present = draft.future.shift()!;
      }),
    ),
}));

export default function App() {
  const { present, set, undo, redo, past, future } = useHistory();

  const onNodesChange: OnNodesChange = useCallback((changes) => {
    set((s) => ({ ...s, nodes: applyNodeChanges(changes, s.nodes) }));
  }, []);
  const onEdgesChange: OnEdgesChange = useCallback((changes) => {
    set((s) => ({ ...s, edges: applyEdgeChanges(changes, s.edges) }));
  }, []);
  const onConnect: OnConnect = useCallback((conn) => {
    set((s) => ({ ...s, edges: addEdge(conn, s.edges) }));
  }, []);

  return (
    <div className="relative h-screen w-screen">
      <div className="absolute top-4 left-4 z-10 flex gap-2">
        <button
          onClick={undo}
          disabled={past.length === 0}
          className="rounded bg-white px-3 py-1 shadow disabled:opacity-50"
        >
          Undo
        </button>
        <button
          onClick={redo}
          disabled={future.length === 0}
          className="rounded bg-white px-3 py-1 shadow disabled:opacity-50"
        >
          Redo
        </button>
      </div>
      <ReactFlow
        nodes={present.nodes}
        edges={present.edges}
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

## Validation

Validate connections before they are created:

```tsx
import { useCallback } from "react";
import { ReactFlow, Background, useNodesState, useEdgesState, addEdge } from "@xyflow/react";
import type { Connection, OnConnect } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initNodes = [
  { id: "1", type: "input" as const, position: { x: 0, y: 0 }, data: { label: "Number (source)" } },
  { id: "2", position: { x: 200, y: 100 }, data: { label: "String (target)" } },
  { id: "3", position: { x: 200, y: 200 }, data: { label: "Number (target)" } },
];

const nodeDataTypes: Record<string, string> = { "1": "number", "2": "string", "3": "number" };

export default function App() {
  const [nodes, , onNodesChange] = useNodesState(initNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const isValidConnection = useCallback((connection: Connection) => {
    const sourceType = nodeDataTypes[connection.source];
    const targetType = nodeDataTypes[connection.target!];
    return sourceType === targetType;
  }, []);

  const onConnect: OnConnect = useCallback((c) => setEdges((e) => addEdge(c, e)), []);

  return (
    <div className="h-screen w-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        isValidConnection={isValidConnection}
        fitView
      >
        <Background />
      </ReactFlow>
    </div>
  );
}
```
