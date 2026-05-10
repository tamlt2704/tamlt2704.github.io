# Chapter 10: Performance

[← Chapter 9: Sub-flows & Groups](chapter-09-groups.md) | [Chapter 11: Export & Serialize →](chapter-11-export.md)

---

## The Problem

A power user imports a 500-node workflow. Dragging a single node stutters. The browser tab eats 2GB of RAM. Kai escalates: "Enterprise customers have massive flows. If it lags, they'll switch to n8n." React Flow can handle thousands of nodes — but only if you avoid common React pitfalls.

## Rule 1: nodeTypes Outside the Component

This is the #1 performance mistake. Defining `nodeTypes` inside a component creates a new object every render, forcing React Flow to unmount and remount every node:

```tsx
// ❌ BAD: new object every render → all nodes remount
function Flow() {
  const nodeTypes = { custom: CustomNode }; // recreated each render!
  return <ReactFlow nodeTypes={nodeTypes} ... />;
}

// ✅ GOOD: stable reference → nodes only update when data changes
const nodeTypes = { custom: CustomNode };

function Flow() {
  return <ReactFlow nodeTypes={nodeTypes} ... />;
}
```

Same rule applies to `edgeTypes`, `defaultEdgeOptions`, and `connectionLineStyle`.

## Rule 2: React.memo for Custom Nodes

Custom nodes re-render when *any* node changes unless you memoize them:

```tsx
import { memo } from 'react';
import { Handle, Position, type NodeProps, type Node } from '@xyflow/react';

type TaskData = { label: string; status: string };
type TaskNode = Node<TaskData, 'task'>;

const TaskNode = memo(function TaskNode({ data }: NodeProps<TaskNode>) {
  return (
    <div style={{ padding: 10, border: '1px solid #ccc', borderRadius: 6 }}>
      <Handle type="target" position={Position.Top} />
      <div>{data.label}</div>
      <small>{data.status}</small>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
});
```

`memo` ensures the node only re-renders when its own props change — not when a sibling node moves.

## Rule 3: useCallback for Handlers

Unstable function references cause unnecessary re-renders:

```tsx
import { useCallback } from 'react';
import { useNodesState, useEdgesState, addEdge, type OnConnect } from '@xyflow/react';

function Flow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // ✅ Stable reference
  const onConnect: OnConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  );

  // ✅ Stable reference
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    console.log('clicked', node.id);
  }, []);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onNodeClick={onNodeClick}
    />
  );
}
```

## Rule 4: Large Graph Strategies

For flows with 500+ nodes, apply these techniques:

```tsx
import { ReactFlow, useNodesState, useEdgesState, type OnConnect } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCallback, useState } from 'react';

function LargeFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(generateNodes(1000));
  const [edges, setEdges, onEdgesChange] = useEdgesState(generateEdges(1000));
  const [isDragging, setIsDragging] = useState(false);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={isDragging ? [] : edges}  // Hide edges during drag
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeDragStart={() => setIsDragging(true)}
        onNodeDragStop={() => setIsDragging(false)}
        minZoom={0.1}
        maxZoom={2}
        fitView
      />
    </div>
  );
}

// Generate test data
function generateNodes(count: number) {
  return Array.from({ length: count }, (_, i) => ({
    id: `${i}`,
    position: { x: (i % 20) * 200, y: Math.floor(i / 20) * 100 },
    data: { label: `Node ${i}` },
  }));
}

function generateEdges(count: number) {
  return Array.from({ length: count - 1 }, (_, i) => ({
    id: `e${i}`,
    source: `${i}`,
    target: `${i + 1}`,
  }));
}
```

## Performance Checklist

| Technique | Impact | When |
|---|---|---|
| `nodeTypes` outside component | Critical | Always |
| `React.memo` on custom nodes | High | Always with custom nodes |
| `useCallback` for handlers | Medium | When passing callbacks |
| Hide edges during drag | High | 200+ edges |
| `elevateEdgesOnSelect: false` | Medium | Many edges |
| Avoid spreading `...node` in renders | Medium | Custom nodes |
| Use `data` for display, not computed values | Medium | Dynamic content |

## Profiling Tips

1. React DevTools Profiler → look for nodes re-rendering on sibling drag
2. Chrome Performance tab → look for long "Render" frames during interaction
3. If edges are the bottleneck, try `type: 'straight'` (cheapest to render)

## What You Learned

- `nodeTypes` defined inside a component is the #1 performance killer
- `React.memo` prevents custom nodes from re-rendering on sibling changes
- `useCallback` stabilizes handler references
- Hiding edges during drag dramatically improves interaction with large graphs
- React Flow handles 1000+ nodes well when you follow these patterns

---

[Chapter 11: Export & Serialize →](chapter-11-export.md)
