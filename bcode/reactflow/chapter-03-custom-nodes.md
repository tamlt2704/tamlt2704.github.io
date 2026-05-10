# Chapter 3: Custom Nodes

[← Chapter 2: Interactivity](chapter-02-interactive.md) | [Chapter 4: Custom Edges →](chapter-04-custom-edges.md)

---

## The Problem

Kai reviews the prototype: "These default nodes all look the same — just text in a box. Users can't tell a trigger from an action from a condition. We need branded components — icons, status badges, configuration previews inside each node." The built-in node types won't cut it. You need custom React components.

## Creating a Custom Node

A custom node is just a React component that receives `NodeProps`:

```tsx
import { Handle, Position, type NodeProps, type Node } from '@xyflow/react';

type ActionNodeData = {
  label: string;
  icon: string;
  status: 'idle' | 'running' | 'done' | 'error';
};

type ActionNode = Node<ActionNodeData, 'action'>;

function ActionNode({ data }: NodeProps<ActionNode>) {
  const statusColors = {
    idle: '#94a3b8',
    running: '#3b82f6',
    done: '#22c55e',
    error: '#ef4444',
  };

  return (
    <div style={{
      padding: 12,
      borderRadius: 8,
      background: 'white',
      border: `2px solid ${statusColors[data.status]}`,
      minWidth: 150,
    }}>
      <Handle type="target" position={Position.Top} />

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 20 }}>{data.icon}</span>
        <span style={{ fontWeight: 600 }}>{data.label}</span>
      </div>
      <div style={{ fontSize: 11, color: statusColors[data.status], marginTop: 4 }}>
        ● {data.status}
      </div>

      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
```

## Multiple Handles

Nodes can have multiple connection points. Use unique `id` props on handles:

```tsx
import { Handle, Position, type NodeProps, type Node } from '@xyflow/react';

type ConditionData = { label: string; condition: string };
type ConditionNode = Node<ConditionData, 'condition'>;

function ConditionNode({ data }: NodeProps<ConditionNode>) {
  return (
    <div style={{
      padding: 12,
      borderRadius: 8,
      background: '#fef3c7',
      border: '2px solid #d97706',
      minWidth: 160,
      textAlign: 'center',
    }}>
      <Handle type="target" position={Position.Top} />

      <div style={{ fontWeight: 600 }}>🔀 {data.label}</div>
      <code style={{ fontSize: 11 }}>{data.condition}</code>

      <Handle type="source" position={Position.Left} id="yes" style={{ background: '#22c55e' }} />
      <Handle type="source" position={Position.Right} id="no" style={{ background: '#ef4444' }} />
    </div>
  );
}
```

## Registering Custom Types

Define `nodeTypes` **outside** your component (critical for performance):

```tsx
import { ReactFlow, useNodesState, useEdgesState, addEdge, type OnConnect } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCallback } from 'react';

const nodeTypes = { action: ActionNode, condition: ConditionNode };

const initialNodes = [
  {
    id: '1',
    type: 'action',
    position: { x: 200, y: 0 },
    data: { label: 'Fetch Data', icon: '🌐', status: 'done' as const },
  },
  {
    id: '2',
    type: 'condition',
    position: { x: 180, y: 150 },
    data: { label: 'Has Email?', condition: 'user.email != null' },
  },
  {
    id: '3',
    type: 'action',
    position: { x: 50, y: 300 },
    data: { label: 'Send Email', icon: '📧', status: 'running' as const },
  },
  {
    id: '4',
    type: 'action',
    position: { x: 350, y: 300 },
    data: { label: 'Log Warning', icon: '⚠️', status: 'idle' as const },
  },
];

const initialEdges = [
  { id: 'e1', source: '1', target: '2' },
  { id: 'e2', source: '2', target: '3', sourceHandle: 'yes' },
  { id: 'e3', source: '2', target: '4', sourceHandle: 'no' },
];

export default function CustomNodesFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const onConnect: OnConnect = useCallback(
    (conn) => setEdges((eds) => addEdge(conn, eds)),
    [setEdges]
  );

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      />
    </div>
  );
}
```

## What You Learned

- Custom nodes are React components receiving `NodeProps<YourNodeType>`
- `Handle` components define connection points with `type` (source/target) and `position`
- Multiple handles need unique `id` props — edges reference them via `sourceHandle`/`targetHandle`
- `nodeTypes` must be defined outside the component to avoid re-renders
- You can put any React content inside a node: icons, badges, forms, charts

---

[Chapter 4: Custom Edges →](chapter-04-custom-edges.md)
