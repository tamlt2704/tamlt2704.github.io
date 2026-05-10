# Chapter 3: Node Configuration Panel

[← Chapter 2: Connections](chapter-02-connections.md) | [Chapter 4: Spring Integration Basics →](chapter-04-spring-integration.md)

---

## Goal

When a user clicks a node, a side panel opens showing configuration fields specific to that node type. Changes update the node's `data.config` in real-time. By the end: each block is configurable, and the full flow graph (with configs) is exportable as JSON.

## Step 1: Zustand Store

Move from React Flow's local state to a shared Zustand store so the config panel and canvas stay in sync.

**src/store/flowStore.ts:**
```ts
import { create } from 'zustand';
import {
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type Connection,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
} from '@xyflow/react';
import { isValidConnection } from '../utils/validation';

interface FlowState {
  nodes: Node[];
  edges: Edge[];
  selectedNodeId: string | null;

  // Actions
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: (connection: Connection) => void;
  addNode: (node: Node) => void;
  selectNode: (nodeId: string | null) => void;
  updateNodeConfig: (nodeId: string, config: Record<string, unknown>) => void;
  getFlowJson: () => FlowExport;
}

export interface FlowExport {
  nodes: Array<{
    id: string;
    type: string;
    category: string;
    position: { x: number; y: number };
    config: Record<string, unknown>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
  }>;
}

export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,

  onNodesChange: (changes) => {
    set({ nodes: applyNodeChanges(changes, get().nodes) });
  },

  onEdgesChange: (changes) => {
    set({ edges: applyEdgeChanges(changes, get().edges) });
  },

  onConnect: (connection) => {
    const { nodes, edges } = get();
    if (isValidConnection(connection, nodes, edges)) {
      set({ edges: addEdge({ ...connection, type: 'flow' }, edges) });
    }
  },

  addNode: (node) => {
    set({ nodes: [...get().nodes, node] });
  },

  selectNode: (nodeId) => {
    set({ selectedNodeId: nodeId });
  },

  updateNodeConfig: (nodeId, config) => {
    set({
      nodes: get().nodes.map(node =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, config } }
          : node
      ),
    });
  },

  getFlowJson: () => {
    const { nodes, edges } = get();
    return {
      nodes: nodes.map(n => ({
        id: n.id,
        type: n.type!,
        category: n.data.category,
        position: n.position,
        config: n.data.config,
      })),
      edges: edges.map(e => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
    };
  },
}));
```

## Step 2: Config Field Definitions

Define what fields each node type exposes:

**src/types/configFields.ts:**
```ts
export interface ConfigField {
  key: string;
  label: string;
  type: 'text' | 'select' | 'number' | 'textarea' | 'code';
  placeholder?: string;
  options?: { value: string; label: string }[];
  required?: boolean;
}

// Config schema per node type
export const NODE_CONFIG_FIELDS: Record<string, ConfigField[]> = {
  'http-inbound': [
    { key: 'path', label: 'Path', type: 'text', placeholder: '/webhook', required: true },
    { key: 'method', label: 'Method', type: 'select', options: [
      { value: 'GET', label: 'GET' },
      { value: 'POST', label: 'POST' },
      { value: 'PUT', label: 'PUT' },
      { value: 'DELETE', label: 'DELETE' },
    ]},
  ],

  'timer': [
    { key: 'cron', label: 'Cron Expression', type: 'text', placeholder: '0 */5 * * * *' },
    { key: 'fixedDelay', label: 'Fixed Delay (ms)', type: 'number', placeholder: '5000' },
  ],

  'file-inbound': [
    { key: 'directory', label: 'Watch Directory', type: 'text', placeholder: '/tmp/input' },
    { key: 'pattern', label: 'File Pattern', type: 'text', placeholder: '*.csv' },
  ],

  'transform': [
    { key: 'expression', label: 'SpEL Expression', type: 'code', placeholder: 'payload.toUpperCase()' },
  ],

  'filter': [
    { key: 'expression', label: 'Condition (SpEL)', type: 'code', placeholder: 'payload.length > 0' },
    { key: 'discardChannel', label: 'Discard Channel', type: 'text', placeholder: 'nullChannel' },
  ],

  'llm-call': [
    { key: 'model', label: 'Model', type: 'select', options: [
      { value: 'gpt-4o', label: 'GPT-4o' },
      { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
      { value: 'claude-sonnet', label: 'Claude Sonnet' },
      { value: 'ollama/llama3', label: 'Ollama Llama 3' },
    ]},
    { key: 'prompt', label: 'Prompt Template', type: 'textarea', placeholder: 'Summarize: {{payload}}' },
    { key: 'temperature', label: 'Temperature', type: 'number', placeholder: '0.7' },
  ],

  'script': [
    { key: 'language', label: 'Language', type: 'select', options: [
      { value: 'groovy', label: 'Groovy' },
      { value: 'javascript', label: 'JavaScript' },
    ]},
    { key: 'code', label: 'Script', type: 'code', placeholder: 'return payload' },
  ],

  'http-outbound': [
    { key: 'url', label: 'URL', type: 'text', placeholder: 'https://api.example.com', required: true },
    { key: 'method', label: 'Method', type: 'select', options: [
      { value: 'GET', label: 'GET' },
      { value: 'POST', label: 'POST' },
      { value: 'PUT', label: 'PUT' },
    ]},
    { key: 'headers', label: 'Headers (JSON)', type: 'textarea', placeholder: '{"Authorization": "Bearer ..."}' },
  ],

  'jdbc-outbound': [
    { key: 'sql', label: 'SQL Statement', type: 'code', placeholder: 'INSERT INTO table(col) VALUES(:payload)' },
    { key: 'dataSource', label: 'Data Source', type: 'select', options: [
      { value: 'default', label: 'Default' },
    ]},
  ],

  'log': [
    { key: 'level', label: 'Log Level', type: 'select', options: [
      { value: 'DEBUG', label: 'DEBUG' },
      { value: 'INFO', label: 'INFO' },
      { value: 'WARN', label: 'WARN' },
      { value: 'ERROR', label: 'ERROR' },
    ]},
    { key: 'expression', label: 'Log Expression', type: 'text', placeholder: 'payload' },
  ],
};
```

## Step 3: The Config Panel Component

**src/components/ConfigPanel.tsx:**
```tsx
import { useFlowStore } from '../store/flowStore';
import { NODE_CONFIG_FIELDS } from '../types/configFields';
import { NODE_CATALOG, CATEGORY_COLORS } from '../types/flow';

export function ConfigPanel() {
  const selectedNodeId = useFlowStore(s => s.selectedNodeId);
  const nodes = useFlowStore(s => s.nodes);
  const updateNodeConfig = useFlowStore(s => s.updateNodeConfig);
  const selectNode = useFlowStore(s => s.selectNode);

  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  if (!selectedNode) {
    return (
      <aside className="w-80 border-l border-gray-200 bg-gray-50 p-6 flex items-center justify-center">
        <p className="text-gray-400 text-sm">Click a node to configure it</p>
      </aside>
    );
  }

  const nodeDef = NODE_CATALOG.find(n => n.type === selectedNode.type);
  const fields = NODE_CONFIG_FIELDS[selectedNode.type!] ?? [];
  const config = (selectedNode.data.config ?? {}) as Record<string, unknown>;
  const colors = CATEGORY_COLORS[nodeDef?.category ?? 'processing'];

  const handleChange = (key: string, value: unknown) => {
    updateNodeConfig(selectedNode.id, { ...config, [key]: value });
  };

  return (
    <aside className="w-80 border-l border-gray-200 bg-white overflow-y-auto">
      {/* Header */}
      <div className={`p-4 border-b ${colors.bg}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">{nodeDef?.icon}</span>
            <div>
              <h3 className={`font-semibold ${colors.text}`}>{nodeDef?.label}</h3>
              <p className="text-xs text-gray-500">{nodeDef?.description}</p>
            </div>
          </div>
          <button
            onClick={() => selectNode(null)}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Config Fields */}
      <div className="p-4 space-y-4">
        {fields.map(field => (
          <div key={field.key}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>

            {field.type === 'text' && (
              <input
                type="text"
                value={(config[field.key] as string) ?? ''}
                onChange={e => handleChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm
                  focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            )}

            {field.type === 'number' && (
              <input
                type="number"
                value={(config[field.key] as number) ?? ''}
                onChange={e => handleChange(field.key, Number(e.target.value))}
                placeholder={field.placeholder}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm
                  focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            )}

            {field.type === 'select' && (
              <select
                value={(config[field.key] as string) ?? ''}
                onChange={e => handleChange(field.key, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm
                  focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {field.options?.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            )}

            {field.type === 'textarea' && (
              <textarea
                value={(config[field.key] as string) ?? ''}
                onChange={e => handleChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm
                  focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
              />
            )}

            {field.type === 'code' && (
              <textarea
                value={(config[field.key] as string) ?? ''}
                onChange={e => handleChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm
                  focus:ring-2 focus:ring-blue-500 focus:border-transparent
                  font-mono bg-gray-900 text-green-400"
              />
            )}
          </div>
        ))}

        {/* Node ID (read-only, for debugging) */}
        <div className="pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-400">Node ID: {selectedNode.id}</p>
          <p className="text-xs text-gray-400">Type: {selectedNode.type}</p>
        </div>
      </div>
    </aside>
  );
}
```

## Step 4: Handle Node Selection

Update the Canvas to detect clicks:

```tsx
// In Canvas.tsx
const selectNode = useFlowStore(s => s.selectNode);

const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
  selectNode(node.id);
}, [selectNode]);

const onPaneClick = useCallback(() => {
  selectNode(null);  // Deselect when clicking empty canvas
}, [selectNode]);

<ReactFlow
  onNodeClick={onNodeClick}
  onPaneClick={onPaneClick}
  // ...
/>
```

## Step 5: Export Flow as JSON

Add a toolbar with a "Deploy" button that exports the current graph:

**src/components/Toolbar.tsx:**
```tsx
import { useFlowStore } from '../store/flowStore';

export function Toolbar() {
  const getFlowJson = useFlowStore(s => s.getFlowJson);
  const nodes = useFlowStore(s => s.nodes);

  const handleDeploy = () => {
    const flow = getFlowJson();
    console.log('Flow JSON:', JSON.stringify(flow, null, 2));

    // Later: POST to /api/flows
    // For now, just show it
    alert(`Flow has ${flow.nodes.length} nodes and ${flow.edges.length} edges.\nCheck console for JSON.`);
  };

  const hasNodes = nodes.length > 0;

  return (
    <div className="h-12 border-b border-gray-200 bg-white px-4 flex items-center justify-between">
      <h1 className="text-lg font-semibold text-gray-800">FlowCraft</h1>
      <div className="flex gap-2">
        <button
          onClick={handleDeploy}
          disabled={!hasNodes}
          className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-md
            hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors"
        >
          🚀 Deploy
        </button>
      </div>
    </div>
  );
}
```

## Step 6: Updated App Layout

**src/App.tsx:**
```tsx
import { ReactFlowProvider } from '@xyflow/react';
import { Sidebar } from './components/Sidebar';
import { Canvas } from './components/Canvas';
import { ConfigPanel } from './components/ConfigPanel';
import { Toolbar } from './components/Toolbar';

export default function App() {
  return (
    <ReactFlowProvider>
      <div className="flex flex-col h-screen">
        <Toolbar />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <Canvas />
          <ConfigPanel />
        </div>
      </div>
    </ReactFlowProvider>
  );
}
```

## The Full UI Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  FlowCraft                                        [🚀 Deploy]   │
├─────────┬────────────────────────────────────┬──────────────────┤
│ SIDEBAR │           CANVAS                    │  CONFIG PANEL   │
│         │                                     │                 │
│ 📥 Input│   ┌──────┐    ┌──────┐    ┌─────┐ │  🌐 HTTP Endpt  │
│ • HTTP  │   │ HTTP │───→│ LLM  │───→│ DB  │ │                 │
│ • Timer │   │  In  │    │ Call │    │Write│ │  Path: /webhook  │
│         │   └──────┘    └──────┘    └─────┘ │  Method: [POST▾] │
│ ⚙️ Proc │                                    │                 │
│ • Trans │                                    │                 │
│ • LLM   │                                    │                 │
│         │                                    │                 │
│ 📤 Out  │                                    │                 │
│ • DB    │                                    │                 │
│ • HTTP  │                                    │                 │
└─────────┴────────────────────────────────────┴──────────────────┘
```

## What the Exported JSON Looks Like

After building a flow and clicking Deploy:

```json
{
  "nodes": [
    {
      "id": "node-1",
      "type": "http-inbound",
      "category": "input",
      "position": { "x": 100, "y": 200 },
      "config": { "path": "/webhook", "method": "POST" }
    },
    {
      "id": "node-2",
      "type": "llm-call",
      "category": "processing",
      "position": { "x": 350, "y": 200 },
      "config": { "model": "gpt-4o", "prompt": "Summarize: {{payload}}", "temperature": 0.7 }
    },
    {
      "id": "node-3",
      "type": "jdbc-outbound",
      "category": "output",
      "position": { "x": 600, "y": 200 },
      "config": { "sql": "INSERT INTO summaries(text) VALUES(:payload)", "dataSource": "default" }
    }
  ],
  "edges": [
    { "id": "e1", "source": "node-1", "target": "node-2" },
    { "id": "e2", "source": "node-2", "target": "node-3" }
  ]
}
```

This is exactly what the Spring Integration backend will consume in Chapter 5.

## Key Takeaways

1. **Zustand** keeps flow state outside React Flow — the config panel and canvas share the same source of truth
2. **Config fields are data-driven** — adding a new node type means adding one entry to `NODE_CONFIG_FIELDS`
3. **The JSON export** is the contract between frontend and backend — design it carefully
4. **Node selection** uses React Flow's `onNodeClick` — simple event handling
5. **The UI is now complete** for an MVP — users can build, configure, and export flows

Next: we switch to the backend and learn Spring Integration fundamentals.

---

[← Chapter 2: Connections](chapter-02-connections.md) | [Chapter 4: Spring Integration Basics →](chapter-04-spring-integration.md)
