# Chapter 7: State Management

[← Chapter 6: Controls & Minimap](chapter-06-controls.md) | [Chapter 8: Validation →](chapter-08-validation.md)

---

## The Problem

The flow editor grows complex. Nodes and edges live in component state, but now you need: undo/redo (users accidentally delete nodes), persistence (refresh shouldn't erase work), and backend sync (save to API). Local `useState` won't scale. Kai says: "If a user hits Ctrl+Z and nothing happens, we've failed."

## Zustand Store for Flow State

Zustand is lightweight, works great with React Flow, and avoids prop-drilling:

```tsx
import { create } from 'zustand';
import {
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type OnConnect,
} from '@xyflow/react';

type HistoryEntry = { nodes: Node[]; edges: Edge[] };

type FlowState = {
  nodes: Node[];
  edges: Edge[];
  history: HistoryEntry[];
  historyIndex: number;
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  pushHistory: () => void;
  undo: () => void;
  redo: () => void;
  save: () => void;
  load: () => void;
};

const initialNodes: Node[] = [
  { id: '1', position: { x: 100, y: 50 }, data: { label: 'Start' }, type: 'input' },
  { id: '2', position: { x: 100, y: 200 }, data: { label: 'End' }, type: 'output' },
];
const initialEdges: Edge[] = [{ id: 'e1-2', source: '1', target: '2' }];

export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: initialNodes,
  edges: initialEdges,
  history: [{ nodes: initialNodes, edges: initialEdges }],
  historyIndex: 0,

  onNodesChange: (changes) => {
    set({ nodes: applyNodeChanges(changes, get().nodes) });
  },
  onEdgesChange: (changes) => {
    set({ edges: applyEdgeChanges(changes, get().edges) });
  },
  onConnect: (connection) => {
    set({ edges: addEdge(connection, get().edges) });
    get().pushHistory();
  },

  pushHistory: () => {
    const { nodes, edges, history, historyIndex } = get();
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push({ nodes: structuredClone(nodes), edges: structuredClone(edges) });
    set({ history: newHistory, historyIndex: newHistory.length - 1 });
  },

  undo: () => {
    const { history, historyIndex } = get();
    if (historyIndex <= 0) return;
    const prev = history[historyIndex - 1];
    set({ nodes: prev.nodes, edges: prev.edges, historyIndex: historyIndex - 1 });
  },

  redo: () => {
    const { history, historyIndex } = get();
    if (historyIndex >= history.length - 1) return;
    const next = history[historyIndex + 1];
    set({ nodes: next.nodes, edges: next.edges, historyIndex: historyIndex + 1 });
  },

  save: () => {
    const { nodes, edges } = get();
    localStorage.setItem('flow', JSON.stringify({ nodes, edges }));
  },

  load: () => {
    const saved = localStorage.getItem('flow');
    if (saved) {
      const { nodes, edges } = JSON.parse(saved);
      set({ nodes, edges });
    }
  },
}));
```

## Using the Store in Your Component

```tsx
import { ReactFlow, Background, Panel, ReactFlowProvider } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useFlowStore } from './store';
import { useEffect } from 'react';

function Flow() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, undo, redo, save, load } =
    useFlowStore();

  useEffect(() => { load(); }, [load]);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Panel position="top-left">
          <button onClick={undo}>↩ Undo</button>
          <button onClick={redo}>↪ Redo</button>
          <button onClick={save}>💾 Save</button>
        </Panel>
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

## Separating UI State from Flow State

Keep selection, panel visibility, and sidebar state in a separate store:

```tsx
type UIState = {
  selectedNodeId: string | null;
  sidebarOpen: boolean;
  setSelectedNode: (id: string | null) => void;
  toggleSidebar: () => void;
};

export const useUIStore = create<UIState>((set) => ({
  selectedNodeId: null,
  sidebarOpen: true,
  setSelectedNode: (id) => set({ selectedNodeId: id }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));
```

## What You Learned

- Zustand provides a clean external store for React Flow state
- `applyNodeChanges` / `applyEdgeChanges` are the low-level functions behind `useNodesState`
- Undo/redo uses a history stack with `structuredClone` snapshots
- `localStorage` persistence is a one-liner with `JSON.stringify`
- Separate UI state (selection, panels) from flow state (nodes, edges) to avoid coupling

---

[Chapter 8: Validation →](chapter-08-validation.md)
