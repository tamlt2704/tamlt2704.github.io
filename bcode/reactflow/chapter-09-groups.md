# Chapter 9: Sub-flows & Groups

[← Chapter 8: Validation](chapter-08-validation.md) | [Chapter 10: Performance →](chapter-10-performance.md)

---

## The Problem

Users build a 5-step "send notification" sequence and reuse it in 3 different workflows. Kai asks: "Can we group nodes together? Like a folder — collapse it, move it as one unit, maybe even nest flows inside flows?" Flat node lists don't express hierarchy. You need parent-child relationships.

## Parent Nodes with parentId

In React Flow, any node can be a parent. Children reference their parent via `parentId` and use relative positioning:

```tsx
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  Background,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const nodes: Node[] = [
  // Parent group node
  {
    id: 'group-1',
    position: { x: 50, y: 50 },
    data: { label: '📦 Notification Pipeline' },
    style: {
      width: 350,
      height: 250,
      background: '#f0f9ff',
      border: '2px dashed #0284c7',
      borderRadius: 12,
      padding: 10,
      fontSize: 14,
    },
    type: 'group',
  },
  // Children — positions are relative to parent
  {
    id: 'child-1',
    position: { x: 20, y: 50 },
    data: { label: 'Format Message' },
    parentId: 'group-1',
    extent: 'parent',
  },
  {
    id: 'child-2',
    position: { x: 20, y: 140 },
    data: { label: 'Send Push' },
    parentId: 'group-1',
    extent: 'parent',
  },
  {
    id: 'child-3',
    position: { x: 180, y: 140 },
    data: { label: 'Send Email' },
    parentId: 'group-1',
    extent: 'parent',
  },
  // External node
  {
    id: 'trigger',
    position: { x: 150, y: 0 },
    data: { label: '⚡ Event Trigger' },
    type: 'input',
  },
  {
    id: 'done',
    position: { x: 150, y: 350 },
    data: { label: '✅ Complete' },
    type: 'output',
  },
];

const edges: Edge[] = [
  { id: 'e0', source: 'trigger', target: 'child-1' },
  { id: 'e1', source: 'child-1', target: 'child-2' },
  { id: 'e2', source: 'child-1', target: 'child-3' },
  { id: 'e3', source: 'child-2', target: 'done' },
  { id: 'e4', source: 'child-3', target: 'done' },
];

export default function GroupFlow() {
  const [nds, , onNodesChange] = useNodesState(nodes);
  const [eds, , onEdgesChange] = useEdgesState(edges);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nds}
        edges={eds}
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

## Key Concepts

| Property | Effect |
|---|---|
| `parentId` | Makes this node a child of the specified parent |
| `extent: 'parent'` | Constrains dragging within parent bounds |
| `type: 'group'` | Built-in type that renders as a container (no handles) |
| Relative position | Child `position` is relative to parent's top-left |

## Drag Children with Parent

When you drag a parent node, all children move with it automatically. That's the default behavior — no extra code needed. Children with `extent: 'parent'` can't be dragged outside the parent boundary.

## Expandable Group Node

Create a custom group node that collapses/expands:

```tsx
import { memo, useState } from 'react';
import { Handle, Position, NodeResizer, type NodeProps, type Node } from '@xyflow/react';

type GroupData = { label: string; childCount: number };
type GroupNode = Node<GroupData, 'expandableGroup'>;

const ExpandableGroup = memo(function ExpandableGroup({ data }: NodeProps<GroupNode>) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div style={{
      padding: 8,
      borderRadius: 8,
      border: '2px dashed #6366f1',
      background: expanded ? '#eef2ff' : '#c7d2fe',
      minWidth: expanded ? 300 : 150,
      minHeight: expanded ? 200 : 50,
      transition: 'all 0.2s',
    }}>
      <NodeResizer minWidth={200} minHeight={100} isVisible={expanded} />
      <Handle type="target" position={Position.Top} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <strong>{data.label}</strong>
        <button onClick={() => setExpanded(!expanded)} style={{ cursor: 'pointer' }}>
          {expanded ? '▼' : '▶'} {data.childCount} steps
        </button>
      </div>

      <Handle type="source" position={Position.Bottom} />
    </div>
  );
});
```

## Node Ordering

Parents must appear **before** their children in the nodes array. React Flow renders nodes in array order, and children need their parent to exist first:

```tsx
// ✅ Correct: parent first
const nodes = [
  { id: 'parent', ... },
  { id: 'child', parentId: 'parent', ... },
];

// ❌ Wrong: child before parent
const nodes = [
  { id: 'child', parentId: 'parent', ... },
  { id: 'parent', ... },
];
```

## What You Learned

- `parentId` creates parent-child relationships between nodes
- `extent: 'parent'` constrains children within the parent boundary
- `type: 'group'` is a built-in container node type (no handles)
- Child positions are relative to the parent's top-left corner
- Dragging a parent moves all children automatically
- Parents must appear before children in the nodes array

---

[Chapter 10: Performance →](chapter-10-performance.md)
