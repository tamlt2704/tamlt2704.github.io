# Chapter 1: Nodes and Edges

[← Chapter 0: Before You Start](chapter-00-overview.md) | [Chapter 2: Interactivity →](chapter-02-interactive.md)

---

## The Problem

Kai pulls up the whiteboard: "Users need to see their workflow as a diagram — triggers on the left, actions in the middle, outputs on the right. Like a flowchart, but pretty." You open a blank canvas. Time to place some nodes.

## Built-in Node Types

React Flow ships three node types out of the box:

| Type | Handles | Use Case |
|---|---|---|
| `input` | Source only (bottom) | Starting points, triggers |
| `default` | Source + Target | Middle steps, actions |
| `output` | Target only (top) | End points, results |

## Built-in Edge Types

| Type | Shape | Use Case |
|---|---|---|
| `default` | Bezier curve | Smooth, organic connections |
| `straight` | Direct line | Minimal, technical diagrams |
| `step` | Right-angle corners | Flowchart style |
| `smoothstep` | Rounded corners | Polished flowchart |

## The Complete Workflow Diagram

```tsx
import { ReactFlow, Background, type Node, type Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const nodes: Node[] = [
  {
    id: 'trigger',
    type: 'input',
    position: { x: 250, y: 0 },
    data: { label: '📩 Form Submitted' },
    style: { background: '#e0f2fe', border: '2px solid #0284c7', borderRadius: 8 },
  },
  {
    id: 'validate',
    type: 'default',
    position: { x: 100, y: 120 },
    data: { label: '✅ Validate Data' },
    className: 'action-node',
  },
  {
    id: 'transform',
    type: 'default',
    position: { x: 400, y: 120 },
    data: { label: '🔄 Transform' },
    style: { background: '#fef3c7', border: '2px solid #d97706', borderRadius: 8 },
  },
  {
    id: 'send-email',
    type: 'default',
    position: { x: 100, y: 250 },
    data: { label: '📧 Send Email' },
    style: { background: '#dcfce7', border: '2px solid #16a34a', borderRadius: 8 },
  },
  {
    id: 'update-crm',
    type: 'default',
    position: { x: 400, y: 250 },
    data: { label: '💾 Update CRM' },
    style: { background: '#dcfce7', border: '2px solid #16a34a', borderRadius: 8 },
  },
  {
    id: 'done',
    type: 'output',
    position: { x: 250, y: 380 },
    data: { label: '🏁 Done' },
    style: { background: '#f3e8ff', border: '2px solid #7c3aed', borderRadius: 8 },
  },
];

const edges: Edge[] = [
  { id: 'e1', source: 'trigger', target: 'validate', type: 'smoothstep' },
  { id: 'e2', source: 'trigger', target: 'transform', type: 'smoothstep' },
  { id: 'e3', source: 'validate', target: 'send-email', type: 'default', animated: true },
  { id: 'e4', source: 'transform', target: 'update-crm', type: 'step' },
  { id: 'e5', source: 'send-email', target: 'done', type: 'straight' },
  { id: 'e6', source: 'update-crm', target: 'done', type: 'straight' },
];

export default function WorkflowDiagram() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.3 }}
      >
        <Background color="#aaa" gap={16} />
      </ReactFlow>
    </div>
  );
}
```

## Styling Nodes

Two approaches — inline `style` or CSS `className`:

```tsx
// Inline style
{ style: { background: '#e0f2fe', border: '2px solid #0284c7', borderRadius: 8 } }

// CSS className (define in your stylesheet)
{ className: 'action-node' }
```

```css
/* styles.css */
.action-node {
  background: #fef9c3;
  border: 2px solid #ca8a04;
  border-radius: 8px;
  font-weight: 600;
}
```

## Positioning Tips

Nodes use absolute `{ x, y }` coordinates. Common patterns:

- **Vertical flow**: Increment `y` by 120–150px per row
- **Horizontal flow**: Increment `x` by 250–300px per column
- **Branching**: Same `y`, different `x` values for siblings

Use `fitView` on `<ReactFlow>` to auto-zoom so all nodes are visible on load.

## What You Learned

- Three built-in node types: `input`, `default`, `output`
- Four edge types: `default` (bezier), `straight`, `step`, `smoothstep`
- Style nodes with `style` (inline) or `className` (CSS)
- `animated: true` on edges adds a dashed flow animation
- `fitView` auto-zooms to show all nodes on mount

---

[Chapter 2: Interactivity →](chapter-02-interactive.md)
