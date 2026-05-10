# Chapter 2: Connection Validation & Edge Styling

[← Chapter 1: Node Palette](chapter-01-node-palette.md) | [Chapter 3: Node Configuration →](chapter-03-node-config.md)

---

## Goal

Prevent invalid connections (Input→Input, Output→Output) and style edges to show data flow direction. By the end: only valid connections are allowed, and edges animate to show flow direction.

## The Validation Rules

```
✅ Input    → Processing   (green to blue)
✅ Input    → Output       (green to orange, skip processing)
✅ Processing → Processing (blue to blue, chaining)
✅ Processing → Output     (blue to orange)

❌ Input    → Input        (two sources, no consumer)
❌ Output   → anything     (output is terminal)
❌ anything → Input        (input is a source, not a target)
❌ Self-loop               (node connecting to itself)
```

## Step 1: Connection Validator

**src/utils/validation.ts:**
```ts
import { type Connection, type Node } from '@xyflow/react';
import { NODE_CATALOG, type NodeCategory } from '../types/flow';

function getNodeCategory(nodeType: string | undefined): NodeCategory | null {
  if (!nodeType) return null;
  const def = NODE_CATALOG.find(n => n.type === nodeType);
  return def?.category ?? null;
}

export function isValidConnection(
  connection: Connection,
  nodes: Node[]
): boolean {
  // No self-loops
  if (connection.source === connection.target) return false;

  const sourceNode = nodes.find(n => n.id === connection.source);
  const targetNode = nodes.find(n => n.id === connection.target);

  const sourceCategory = getNodeCategory(sourceNode?.type);
  const targetCategory = getNodeCategory(targetNode?.type);

  if (!sourceCategory || !targetCategory) return false;

  // Output nodes cannot be a source
  if (sourceCategory === 'output') return false;

  // Input nodes cannot be a target
  if (targetCategory === 'input') return false;

  // All other combinations are valid
  return true;
}
```

## Step 2: Apply Validation to Canvas

Update `Canvas.tsx` to use the validator:

```tsx
import { isValidConnection } from '../utils/validation';

export function Canvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Validate before allowing connection
  const onConnect = useCallback(
    (connection: Connection) => {
      if (isValidConnection(connection, nodes)) {
        setEdges((eds) => addEdge({
          ...connection,
          animated: true,
          style: { stroke: '#6b7280', strokeWidth: 2 },
        }, eds));
      }
    },
    [setEdges, nodes]
  );

  // Show visual feedback during drag
  const isValidConnectionCheck = useCallback(
    (connection: Connection) => isValidConnection(connection, nodes),
    [nodes]
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      isValidConnection={isValidConnectionCheck}  // ← React Flow uses this for visual feedback
      nodeTypes={nodeTypes}
      // ... rest
    >
      {/* ... */}
    </ReactFlow>
  );
}
```

When `isValidConnection` returns `false`, React Flow:
- Shows the connection line in red
- Prevents the edge from being created
- The handle doesn't "snap" to invalid targets

## Step 3: Custom Edge with Animation

Create an animated edge that shows data flowing from source to target:

**src/components/edges/FlowEdge.tsx:**
```tsx
import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  type EdgeProps,
} from '@xyflow/react';

export function FlowEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          strokeWidth: 2,
          stroke: '#6b7280',
        }}
      />
      {/* Animated dot traveling along the edge */}
      <circle r="4" fill="#3b82f6">
        <animateMotion
          dur="2s"
          repeatCount="indefinite"
          path={edgePath}
        />
      </circle>
      {/* Optional: message count label */}
      {data?.messageCount != null && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="bg-white border border-gray-300 rounded px-2 py-0.5 text-xs text-gray-600"
          >
            {data.messageCount} msgs
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
```

Register it:

**src/components/edgeTypes.ts:**
```ts
import { type EdgeTypes } from '@xyflow/react';
import { FlowEdge } from './edges/FlowEdge';

export const edgeTypes: EdgeTypes = {
  flow: FlowEdge,
};
```

Use in Canvas:
```tsx
import { edgeTypes } from './edgeTypes';

// In onConnect, set the edge type:
const onConnect = useCallback(
  (connection: Connection) => {
    if (isValidConnection(connection, nodes)) {
      setEdges((eds) => addEdge({
        ...connection,
        type: 'flow',  // ← use our custom edge
      }, eds));
    }
  },
  [setEdges, nodes]
);

// Pass to ReactFlow:
<ReactFlow
  edgeTypes={edgeTypes}
  defaultEdgeOptions={{ type: 'flow' }}
  // ...
/>
```

## Step 4: Connection Line Styling

Style the line that appears while the user is dragging a connection:

```tsx
import { type ConnectionLineComponentProps } from '@xyflow/react';

function ConnectionLine({
  fromX,
  fromY,
  toX,
  toY,
}: ConnectionLineComponentProps) {
  return (
    <g>
      <path
        fill="none"
        stroke="#3b82f6"
        strokeWidth={2}
        strokeDasharray="5,5"
        d={`M${fromX},${fromY} C${fromX + 50},${fromY} ${toX - 50},${toY} ${toX},${toY}`}
      />
      <circle cx={toX} cy={toY} r={4} fill="#3b82f6" />
    </g>
  );
}

// In ReactFlow:
<ReactFlow
  connectionLineComponent={ConnectionLine}
  // ...
/>
```

## Step 5: Prevent Duplicate Connections

A user shouldn't connect the same two nodes twice:

```ts
export function isValidConnection(
  connection: Connection,
  nodes: Node[],
  edges: Edge[]  // ← add edges parameter
): boolean {
  // ... existing checks ...

  // No duplicate edges
  const duplicate = edges.some(
    e => e.source === connection.source && e.target === connection.target
  );
  if (duplicate) return false;

  return true;
}
```

## Step 6: Visual Feedback on Handles

Make handles glow when a valid connection is being dragged near them:

```css
/* src/styles/handles.css */
.react-flow__handle {
  transition: all 0.2s ease;
}

.react-flow__handle.connecting {
  background: #3b82f6 !important;
}

.react-flow__handle.valid {
  box-shadow: 0 0 6px 2px rgba(59, 130, 246, 0.5);
}
```

## What You Have Now

```
User drags from HTTP Endpoint (green, right handle)
  → Dashed blue line follows cursor
  → Hovers over Transform (blue, left handle glows)
  → Drops: animated edge appears with flowing dot
  → Tries to connect to another Input node: RED line, won't connect

User drags from DB Write (orange, no right handle)
  → Can't start a connection (no source handle exists)
```

## The Validation Matrix

| Source ↓ / Target → | Input | Processing | Output |
|---|---|---|---|
| **Input** | ❌ | ✅ | ✅ |
| **Processing** | ❌ | ✅ | ✅ |
| **Output** | ❌ | ❌ | ❌ |

This is enforced at two levels:
1. **Handle placement**: Input nodes have no target handle, Output nodes have no source handle
2. **`isValidConnection`**: Catches edge cases (like if you add handles for future features)

## Key Takeaways

1. **`isValidConnection` prop** — React Flow calls this during drag to show red/green feedback
2. **Custom edges** — Full React/SVG control over how connections look
3. **`animateMotion`** — SVG animation that moves a dot along the edge path (zero JS overhead)
4. **Double validation** — Handle placement prevents most invalid connections; the validator catches the rest
5. **Edge types** — Like node types, register once and reference by string key

---

[← Chapter 1: Node Palette](chapter-01-node-palette.md) | [Chapter 3: Node Configuration →](chapter-03-node-config.md)
