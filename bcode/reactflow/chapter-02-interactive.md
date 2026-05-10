# Chapter 2: Interactivity

[← Chapter 1: Nodes and Edges](chapter-01-basics.md) | [Chapter 3: Custom Nodes →](chapter-03-custom-nodes.md)

---

## The Problem

Kai watches a user test: "They're trying to drag the nodes. They're trying to draw connections. Nothing happens." Your static diagram from Chapter 1 is read-only. Users expect Figma-level interactivity — drag to reposition, draw edges between nodes, select and delete. Time to wire up the event handlers.

## The State Hooks

React Flow provides two hooks that manage node/edge arrays and produce the change handlers you need:

```tsx
import {
  ReactFlow,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  type Node,
  type Edge,
  type OnConnect,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCallback } from 'react';

const initialNodes: Node[] = [
  { id: '1', position: { x: 100, y: 50 }, data: { label: '📩 Trigger' }, type: 'input' },
  { id: '2', position: { x: 100, y: 200 }, data: { label: '⚙️ Process' } },
  { id: '3', position: { x: 100, y: 350 }, data: { label: '📧 Notify' }, type: 'output' },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
];

export default function InteractiveFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect: OnConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  );

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
      </ReactFlow>
    </div>
  );
}
```

## What Each Piece Does

| API | Purpose |
|---|---|
| `useNodesState` | Returns `[nodes, setNodes, onNodesChange]` — manages position, selection, removal |
| `useEdgesState` | Returns `[edges, setEdges, onEdgesChange]` — manages selection, removal |
| `onNodesChange` | Handles drag, select, remove events for nodes |
| `onEdgesChange` | Handles select, remove events for edges |
| `onConnect` | Fires when user draws an edge from source handle to target handle |
| `addEdge` | Utility that appends a new edge (with auto-generated id) to the array |

## Controlling Interactions Per-Node

You can disable interactions on individual nodes:

```tsx
const nodes: Node[] = [
  {
    id: 'locked',
    position: { x: 250, y: 0 },
    data: { label: '🔒 Locked Trigger' },
    draggable: false,    // Can't be moved
    selectable: true,    // Can still be selected
    deletable: false,    // Can't be deleted with Backspace
    connectable: true,   // Can still connect edges
  },
];
```

## Handling Callbacks

Beyond `onConnect`, React Flow fires callbacks for common interactions:

```tsx
<ReactFlow
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  onConnect={onConnect}
  onNodeClick={(event, node) => console.log('Clicked:', node.id)}
  onNodeDragStop={(event, node) => console.log('Dropped at:', node.position)}
  onEdgeClick={(event, edge) => console.log('Edge:', edge.id)}
  onPaneClick={() => console.log('Clicked empty canvas')}
  deleteKeyCode="Backspace"
/>
```

## The Interaction Flow

```
User drags node
  → onNodesChange fires with type: 'position'
  → useNodesState updates node.position
  → React re-renders node at new position

User draws edge (handle → handle)
  → onConnect fires with { source, target, sourceHandle, targetHandle }
  → addEdge creates new edge object
  → setEdges appends it to the array

User presses Backspace on selected node/edge
  → onNodesChange/onEdgesChange fires with type: 'remove'
  → useNodesState/useEdgesState removes the item
```

## What You Learned

- `useNodesState` and `useEdgesState` manage the flow's mutable state
- `onNodesChange` handles drag, select, and remove in one callback
- `onConnect` + `addEdge` lets users draw new connections
- Per-node flags (`draggable`, `deletable`, `connectable`) control individual behavior
- Callbacks like `onNodeClick` and `onPaneClick` let you build custom interactions

---

[Chapter 3: Custom Nodes →](chapter-03-custom-nodes.md)
