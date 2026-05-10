# Chapter 8: Validation

[← Chapter 7: State Management](chapter-07-state.md) | [Chapter 9: Sub-flows & Groups →](chapter-09-groups.md)

---

## The Problem

Users connect anything to anything. A trigger connects to itself. Two edges go to the same handle. An output connects back to an input creating a cycle. Kai's bug report: "A user connected 'Send Email' to 'Send Email' and the workflow ran forever. We need connection rules."

## isValidConnection

The `isValidConnection` prop on `<ReactFlow>` is your gatekeeper. Return `false` to reject a connection:

```tsx
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type OnConnect,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCallback } from 'react';

const nodes: Node[] = [
  { id: '1', position: { x: 100, y: 0 }, data: { label: 'Trigger' }, type: 'input' },
  { id: '2', position: { x: 0, y: 150 }, data: { label: 'Action A' } },
  { id: '3', position: { x: 200, y: 150 }, data: { label: 'Action B' } },
  { id: '4', position: { x: 100, y: 300 }, data: { label: 'Output' }, type: 'output' },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
];

export default function ValidationFlow() {
  const [nds, , onNodesChange] = useNodesState(nodes);
  const [eds, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect: OnConnect = useCallback(
    (conn) => setEdges((edges) => addEdge(conn, edges)),
    [setEdges]
  );

  const isValidConnection = useCallback(
    (connection: Connection) => {
      // Rule 1: No self-connections
      if (connection.source === connection.target) return false;

      // Rule 2: No duplicate edges
      const exists = eds.some(
        (e) =>
          e.source === connection.source &&
          e.target === connection.target &&
          e.sourceHandle === connection.sourceHandle &&
          e.targetHandle === connection.targetHandle
      );
      if (exists) return false;

      // Rule 3: No connecting output nodes back to input nodes
      const sourceNode = nds.find((n) => n.id === connection.source);
      const targetNode = nds.find((n) => n.id === connection.target);
      if (sourceNode?.type === 'output' || targetNode?.type === 'input') return false;

      return true;
    },
    [eds, nds]
  );

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nds}
        edges={eds}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        isValidConnection={isValidConnection}
        fitView
      />
    </div>
  );
}
```

## Max Connections Per Handle

Limit how many edges can connect to a single handle using the `Handle` component:

```tsx
import { Handle, Position } from '@xyflow/react';

function LimitedNode({ data }: { data: { label: string } }) {
  return (
    <div style={{ padding: 10, border: '1px solid #ccc', borderRadius: 6 }}>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={true}
      />
      <div>{data.label}</div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectableStart={true}
        isConnectableEnd={false}
      />
    </div>
  );
}
```

For dynamic max-connection logic, count existing edges in `isValidConnection`:

```tsx
const isValidConnection = useCallback(
  (connection: Connection) => {
    const MAX_CONNECTIONS = 2;
    const targetEdges = eds.filter(
      (e) => e.target === connection.target && e.targetHandle === connection.targetHandle
    );
    if (targetEdges.length >= MAX_CONNECTIONS) return false;
    return true;
  },
  [eds]
);
```

## Visual Feedback on Invalid Drag

React Flow dims the connection line when `isValidConnection` returns `false`. You can enhance this with CSS:

```css
/* The connection line while dragging */
.react-flow__connection-path {
  stroke: #3b82f6;
  stroke-width: 2;
}

/* When hovering over an invalid target, the handle gets this class */
.react-flow__handle.connectingto {
  background: #ef4444;
}

/* Valid target handle */
.react-flow__handle.valid {
  background: #22c55e;
}
```

## Handle Types for Typed Connections

Use `sourceHandle` and `targetHandle` IDs to enforce type compatibility:

```tsx
const isValidConnection = useCallback(
  (connection: Connection) => {
    // Only allow "data" outputs to connect to "data" inputs
    const sourceType = connection.sourceHandle?.split('-')[0]; // e.g., "data-out" → "data"
    const targetType = connection.targetHandle?.split('-')[0]; // e.g., "data-in" → "data"
    return sourceType === targetType;
  },
  []
);
```

## What You Learned

- `isValidConnection` is the single callback for all connection validation
- Prevent self-connections by comparing `source` and `target`
- Prevent duplicates by checking existing edges array
- Limit connections per handle by counting edges in the validator
- Handle IDs enable typed connections (data → data, trigger → trigger)
- React Flow provides visual feedback automatically when connections are invalid

---

[Chapter 9: Sub-flows & Groups →](chapter-09-groups.md)
