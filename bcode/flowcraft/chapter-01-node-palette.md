# Chapter 1: Node Palette & Canvas

[← Chapter 0: Architecture](chapter-00-architecture.md) | [Chapter 2: Connections →](chapter-02-connections.md)

---

## Goal

Build a sidebar with draggable blocks (Input, Processing, Output) and a React Flow canvas where users drop them. By the end: users can drag blocks onto the canvas and see them rendered with category-specific colors and handles.

## Step 1: Define the Node Types

**src/types/flow.ts:**
```ts
export type NodeCategory = 'input' | 'processing' | 'output';

export interface NodeTypeDefinition {
  type: string;
  label: string;
  category: NodeCategory;
  description: string;
  icon: string; // emoji for now, swap to icons later
  defaultConfig: Record<string, unknown>;
}

// The node catalog — all available blocks
export const NODE_CATALOG: NodeTypeDefinition[] = [
  // Inputs
  {
    type: 'http-inbound',
    label: 'HTTP Endpoint',
    category: 'input',
    description: 'Receives HTTP requests',
    icon: '🌐',
    defaultConfig: { path: '/webhook', method: 'POST' },
  },
  {
    type: 'timer',
    label: 'Timer',
    category: 'input',
    description: 'Triggers on a schedule',
    icon: '⏰',
    defaultConfig: { cron: '0 * * * * *' },
  },
  {
    type: 'file-inbound',
    label: 'File Watcher',
    category: 'input',
    description: 'Watches a directory for new files',
    icon: '📁',
    defaultConfig: { directory: '/tmp/input', pattern: '*.csv' },
  },

  // Processing
  {
    type: 'transform',
    label: 'Transform',
    category: 'processing',
    description: 'Transform the message payload',
    icon: '🔄',
    defaultConfig: { expression: 'payload.toUpperCase()' },
  },
  {
    type: 'filter',
    label: 'Filter',
    category: 'processing',
    description: 'Pass or discard based on condition',
    icon: '🔍',
    defaultConfig: { expression: 'payload.length > 0' },
  },
  {
    type: 'llm-call',
    label: 'LLM Call',
    category: 'processing',
    description: 'Send to an LLM and get response',
    icon: '🤖',
    defaultConfig: { model: 'gpt-4o', prompt: 'Summarize: {{payload}}' },
  },
  {
    type: 'script',
    label: 'Script',
    category: 'processing',
    description: 'Run custom Groovy/JS code',
    icon: '📝',
    defaultConfig: { language: 'groovy', code: 'return payload' },
  },

  // Outputs
  {
    type: 'http-outbound',
    label: 'HTTP Call',
    category: 'output',
    description: 'Make an outbound HTTP request',
    icon: '📤',
    defaultConfig: { url: 'https://api.example.com', method: 'POST' },
  },
  {
    type: 'jdbc-outbound',
    label: 'Database Write',
    category: 'output',
    description: 'Write to a SQL database',
    icon: '🗄️',
    defaultConfig: { sql: 'INSERT INTO table(col) VALUES(:payload)' },
  },
  {
    type: 'log',
    label: 'Logger',
    category: 'output',
    description: 'Log the message',
    icon: '📋',
    defaultConfig: { level: 'INFO' },
  },
];

// Color scheme per category
export const CATEGORY_COLORS: Record<NodeCategory, { bg: string; border: string; text: string }> = {
  input:      { bg: 'bg-green-50',  border: 'border-green-400', text: 'text-green-700' },
  processing: { bg: 'bg-blue-50',   border: 'border-blue-400',  text: 'text-blue-700' },
  output:     { bg: 'bg-orange-50', border: 'border-orange-400', text: 'text-orange-700' },
};
```

## Step 2: The Sidebar (Node Palette)

**src/components/Sidebar.tsx:**
```tsx
import { NODE_CATALOG, CATEGORY_COLORS, NodeCategory } from '../types/flow';

const categories: { key: NodeCategory; label: string }[] = [
  { key: 'input', label: '📥 Input' },
  { key: 'processing', label: '⚙️ Processing' },
  { key: 'output', label: '📤 Output' },
];

export function Sidebar() {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    // Store the node type in the drag event
    event.dataTransfer.setData('application/flowcraft-node', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="w-64 border-r border-gray-200 bg-white p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold mb-4">Blocks</h2>

      {categories.map(({ key, label }) => (
        <div key={key} className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">{label}</h3>
          <div className="space-y-2">
            {NODE_CATALOG.filter(n => n.category === key).map(node => {
              const colors = CATEGORY_COLORS[key];
              return (
                <div
                  key={node.type}
                  draggable
                  onDragStart={(e) => onDragStart(e, node.type)}
                  className={`
                    p-3 rounded-lg border-2 cursor-grab active:cursor-grabbing
                    ${colors.bg} ${colors.border}
                    hover:shadow-md transition-shadow
                  `}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{node.icon}</span>
                    <div>
                      <div className={`text-sm font-medium ${colors.text}`}>
                        {node.label}
                      </div>
                      <div className="text-xs text-gray-500">
                        {node.description}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </aside>
  );
}
```

## Step 3: Custom Node Components

Each category gets its own React Flow node component with appropriate handles.

**src/components/nodes/InputNode.tsx:**
```tsx
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { CATEGORY_COLORS } from '../../types/flow';

export function InputNode({ data }: NodeProps) {
  const colors = CATEGORY_COLORS.input;

  return (
    <div className={`px-4 py-3 rounded-lg border-2 shadow-sm min-w-[150px]
      ${colors.bg} ${colors.border}`}>
      <div className="flex items-center gap-2">
        <span>{data.icon}</span>
        <span className={`text-sm font-medium ${colors.text}`}>{data.label}</span>
      </div>
      {data.subtitle && (
        <div className="text-xs text-gray-500 mt-1">{data.subtitle}</div>
      )}
      {/* Input nodes only have an output handle (right side) */}
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-green-500 !w-3 !h-3"
      />
    </div>
  );
}
```

**src/components/nodes/ProcessNode.tsx:**
```tsx
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { CATEGORY_COLORS } from '../../types/flow';

export function ProcessNode({ data }: NodeProps) {
  const colors = CATEGORY_COLORS.processing;

  return (
    <div className={`px-4 py-3 rounded-lg border-2 shadow-sm min-w-[150px]
      ${colors.bg} ${colors.border}`}>
      {/* Processing nodes have both input (left) and output (right) */}
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-blue-500 !w-3 !h-3"
      />
      <div className="flex items-center gap-2">
        <span>{data.icon}</span>
        <span className={`text-sm font-medium ${colors.text}`}>{data.label}</span>
      </div>
      {data.subtitle && (
        <div className="text-xs text-gray-500 mt-1">{data.subtitle}</div>
      )}
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-blue-500 !w-3 !h-3"
      />
    </div>
  );
}
```

**src/components/nodes/OutputNode.tsx:**
```tsx
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { CATEGORY_COLORS } from '../../types/flow';

export function OutputNode({ data }: NodeProps) {
  const colors = CATEGORY_COLORS.output;

  return (
    <div className={`px-4 py-3 rounded-lg border-2 shadow-sm min-w-[150px]
      ${colors.bg} ${colors.border}`}>
      {/* Output nodes only have an input handle (left side) */}
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-orange-500 !w-3 !h-3"
      />
      <div className="flex items-center gap-2">
        <span>{data.icon}</span>
        <span className={`text-sm font-medium ${colors.text}`}>{data.label}</span>
      </div>
      {data.subtitle && (
        <div className="text-xs text-gray-500 mt-1">{data.subtitle}</div>
      )}
    </div>
  );
}
```

## Step 4: Register Custom Node Types

**src/components/nodeTypes.ts:**
```ts
import { type NodeTypes } from '@xyflow/react';
import { InputNode } from './nodes/InputNode';
import { ProcessNode } from './nodes/ProcessNode';
import { OutputNode } from './nodes/OutputNode';

// Map node categories to components
// All input-type nodes use InputNode, etc.
export const nodeTypes: NodeTypes = {
  'http-inbound': InputNode,
  'timer': InputNode,
  'file-inbound': InputNode,
  'transform': ProcessNode,
  'filter': ProcessNode,
  'llm-call': ProcessNode,
  'script': ProcessNode,
  'http-outbound': OutputNode,
  'jdbc-outbound': OutputNode,
  'log': OutputNode,
};
```

## Step 5: The Canvas with Drop Support

**src/components/Canvas.tsx:**
```tsx
import { useCallback } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type Node,
} from '@xyflow/react';
import { nodeTypes } from './nodeTypes';
import { NODE_CATALOG } from '../types/flow';

let nodeId = 0;
const getNodeId = () => `node-${++nodeId}`;

export function Canvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Handle new connections between nodes
  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds));
    },
    [setEdges]
  );

  // Handle drop from sidebar
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const nodeType = event.dataTransfer.getData('application/flowcraft-node');
      if (!nodeType) return;

      // Find the node definition from catalog
      const nodeDef = NODE_CATALOG.find(n => n.type === nodeType);
      if (!nodeDef) return;

      // Get the drop position on the canvas
      // Note: in production, use reactFlowInstance.screenToFlowPosition()
      const position = {
        x: event.clientX - 300, // offset for sidebar width
        y: event.clientY - 50,
      };

      const newNode: Node = {
        id: getNodeId(),
        type: nodeType,
        position,
        data: {
          label: nodeDef.label,
          icon: nodeDef.icon,
          category: nodeDef.category,
          config: { ...nodeDef.defaultConfig },
        },
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [setNodes]
  );

  return (
    <div className="flex-1 h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDragOver={onDragOver}
        onDrop={onDrop}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background gap={20} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            switch (node.data?.category) {
              case 'input': return '#4ade80';
              case 'processing': return '#60a5fa';
              case 'output': return '#fb923c';
              default: return '#e5e7eb';
            }
          }}
        />
      </ReactFlow>
    </div>
  );
}
```

## Step 6: Wire It Together

**src/App.tsx:**
```tsx
import { ReactFlowProvider } from '@xyflow/react';
import { Sidebar } from './components/Sidebar';
import { Canvas } from './components/Canvas';

export default function App() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <ReactFlowProvider>
        <Canvas />
      </ReactFlowProvider>
    </div>
  );
}
```

## What You Have Now

```
┌──────────────────────────────────────────────────────────┐
│  ┌─────────┐  ┌──────────────────────────────────────┐  │
│  │ SIDEBAR │  │          CANVAS                       │  │
│  │         │  │                                       │  │
│  │ 📥 Input│  │   ┌──────────┐     ┌──────────┐     │  │
│  │ • HTTP  │  │   │ 🌐 HTTP  │────→│ 🔄 Trans │──→  │  │
│  │ • Timer │  │   │  Endpoint│     │  form    │     │  │
│  │ • File  │  │   └──────────┘     └──────────┘     │  │
│  │         │  │                                       │  │
│  │ ⚙️ Proc │  │                    ┌──────────┐     │  │
│  │ • Trans │  │               ──→  │ 🗄️ DB    │     │  │
│  │ • Filter│  │                    │  Write   │     │  │
│  │ • LLM   │  │                    └──────────┘     │  │
│  │         │  │                                       │  │
│  │ 📤 Out  │  │   [Background grid]                  │  │
│  │ • HTTP  │  │   [MiniMap]  [Controls]              │  │
│  │ • DB    │  │                                       │  │
│  │ • Log   │  └──────────────────────────────────────┘  │
│  └─────────┘                                            │
└──────────────────────────────────────────────────────────┘
```

Users can:
- ✅ See categorized blocks in the sidebar
- ✅ Drag blocks onto the canvas
- ✅ Blocks render with category-specific colors and handles
- ✅ Connect blocks by dragging from handle to handle
- ✅ Pan, zoom, select, delete

## Improving the Drop Position

The naive `event.clientX` approach doesn't account for zoom/pan. Here's the proper way:

```tsx
import { useReactFlow } from '@xyflow/react';

// Inside Canvas component:
const { screenToFlowPosition } = useReactFlow();

const onDrop = useCallback((event: React.DragEvent) => {
  event.preventDefault();
  const nodeType = event.dataTransfer.getData('application/flowcraft-node');
  if (!nodeType) return;

  // This correctly accounts for zoom and pan
  const position = screenToFlowPosition({
    x: event.clientX,
    y: event.clientY,
  });

  // ... create node with this position
}, [screenToFlowPosition, setNodes]);
```

## Key Takeaways

1. **Drag-and-drop** uses the HTML5 Drag API — store data in `dataTransfer`, handle `onDrop` on the canvas
2. **Custom nodes** are just React components — React Flow passes `data` as props
3. **Handles** define connection points — `type="source"` (output) and `type="target"` (input)
4. **Node types** map string keys to components — register them once, use everywhere
5. **Category colors** give instant visual feedback about what kind of block you're looking at

Next chapter: we add connection validation (Input can't connect to Input) and edge styling.

---

[← Chapter 0: Architecture](chapter-00-architecture.md) | [Chapter 2: Connections →](chapter-02-connections.md)
