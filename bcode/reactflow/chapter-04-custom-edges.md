# Chapter 4: Custom Edges

[← Chapter 3: Custom Nodes](chapter-03-custom-nodes.md) | [Chapter 5: Layout →](chapter-05-layout.md)

---

## The Problem

Kai watches a user stare at a complex flow: "Which edge is which? They all look the same. Users need labels on connections, arrows showing direction, and a way to delete edges without hunting for keyboard shortcuts." Default edges are functional but featureless. You need custom edges with labels, animations, and interactive controls.

## Edge Path Utilities

React Flow provides path-generation functions you can use in custom edges:

```tsx
import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  getSmoothStepPath,
  getStraightPath,
  type EdgeProps,
  type Edge,
} from '@xyflow/react';
```

## Custom Edge with Delete Button

```tsx
import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  useReactFlow,
  type EdgeProps,
  type Edge,
} from '@xyflow/react';

type DeleteEdgeData = { label?: string };
type DeleteEdge = Edge<DeleteEdgeData, 'deletable'>;

function DeletableEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  style,
}: EdgeProps<DeleteEdge>) {
  const { setEdges } = useReactFlow();
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX, sourceY, sourcePosition,
    targetX, targetY, targetPosition,
  });

  const onDelete = () => {
    setEdges((edges) => edges.filter((e) => e.id !== id));
  };

  return (
    <>
      <BaseEdge path={edgePath} style={style} />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            pointerEvents: 'all',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          {data?.label && (
            <span style={{ fontSize: 11, background: 'white', padding: '2px 6px', borderRadius: 4 }}>
              {data.label}
            </span>
          )}
          <button
            onClick={onDelete}
            style={{
              width: 20, height: 20, borderRadius: '50%',
              background: '#ef4444', color: 'white', border: 'none',
              cursor: 'pointer', fontSize: 12, lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
```

## Animated Edge with Arrow Markers

```tsx
import { type Edge } from '@xyflow/react';
import { MarkerType } from '@xyflow/react';

const edges: Edge[] = [
  {
    id: 'e1',
    source: '1',
    target: '2',
    animated: true,
    label: 'async',
    style: { stroke: '#3b82f6', strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
  },
  {
    id: 'e2',
    source: '2',
    target: '3',
    type: 'smoothstep',
    label: 'on success',
    style: { stroke: '#22c55e', strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#22c55e' },
  },
];
```

## Putting It Together

```tsx
import { ReactFlow, useNodesState, useEdgesState, MarkerType, type Node, type Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const edgeTypes = { deletable: DeletableEdge };

const nodes: Node[] = [
  { id: '1', type: 'input', position: { x: 200, y: 0 }, data: { label: 'API Request' } },
  { id: '2', position: { x: 200, y: 150 }, data: { label: 'Process' } },
  { id: '3', type: 'output', position: { x: 200, y: 300 }, data: { label: 'Response' } },
];

const initialEdges: Edge[] = [
  {
    id: 'e1',
    source: '1',
    target: '2',
    type: 'deletable',
    data: { label: 'POST /data' },
    animated: true,
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: 'e2',
    source: '2',
    target: '3',
    type: 'deletable',
    data: { label: '200 OK' },
    style: { stroke: '#22c55e' },
  },
];

export default function CustomEdgesFlow() {
  const [nds, , onNodesChange] = useNodesState(nodes);
  const [eds, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nds}
        edges={eds}
        edgeTypes={edgeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      />
    </div>
  );
}
```

## What You Learned

- Custom edges use `getBezierPath` / `getSmoothStepPath` to compute SVG paths
- `BaseEdge` renders the path; `EdgeLabelRenderer` positions HTML overlays on edges
- `MarkerType.ArrowClosed` adds directional arrows to edge endpoints
- `animated: true` adds a dashed-line animation to any edge
- `edgeTypes` (like `nodeTypes`) must be defined outside the component
- `useReactFlow()` gives access to `setEdges` for programmatic edge removal

---

[Chapter 5: Layout →](chapter-05-layout.md)
