# Chapter 9: Deploy & Execute from UI

[← Chapter 8: Flow CRUD](chapter-08-flow-crud.md) | [Chapter 10: Live Monitoring →](chapter-10-monitoring.md)

---

## Goal

Wire the full save → deploy → test cycle in the UI. Users can save flows, see them in a list, deploy/undeploy, and test deployed flows directly from the browser. By the end: the complete user journey works end-to-end.

## Step 1: Flow List Panel

A drawer/modal showing all saved flows with their status:

**src/components/FlowList.tsx:**
```tsx
import { useEffect, useState } from 'react';
import { listFlows, deleteFlow, deployFlow, undeployFlow, loadFlow, type FlowSummary } from '../api/client';
import { useFlowStore } from '../store/flowStore';

interface Props {
  open: boolean;
  onClose: () => void;
}

export function FlowList({ open, onClose }: Props) {
  const [flows, setFlows] = useState<FlowSummary[]>([]);
  const [loading, setLoading] = useState(false);

  const loadFlowIntoCanvas = useFlowStore(s => s.loadFromJson);

  useEffect(() => {
    if (open) refresh();
  }, [open]);

  const refresh = async () => {
    setLoading(true);
    const data = await listFlows();
    setFlows(data);
    setLoading(false);
  };

  const handleLoad = async (flowId: string) => {
    const flow = await loadFlow(flowId);
    loadFlowIntoCanvas(flow);
    onClose();
  };

  const handleDeploy = async (flowId: string) => {
    await deployFlow(flowId);
    refresh();
  };

  const handleUndeploy = async (flowId: string) => {
    await undeployFlow(flowId);
    refresh();
  };

  const handleDelete = async (flowId: string) => {
    if (confirm('Delete this flow?')) {
      await deleteFlow(flowId);
      refresh();
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl w-[600px] max-h-[80vh] flex flex-col">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-semibold">My Flows</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {loading && <p className="text-gray-400">Loading...</p>}

          {flows.length === 0 && !loading && (
            <p className="text-gray-400 text-center py-8">No flows yet. Build one!</p>
          )}

          <div className="space-y-3">
            {flows.map(flow => (
              <div key={flow.id} className="border rounded-lg p-4 hover:border-blue-300 transition">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{flow.name}</h3>
                    <p className="text-xs text-gray-500">
                      Updated: {new Date(flow.updatedAt).toLocaleString()}
                    </p>
                  </div>
                  <StatusBadge status={flow.status} />
                </div>

                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => handleLoad(flow.id)}
                    className="px-3 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
                  >
                    📂 Open
                  </button>

                  {flow.status === 'RUNNING' ? (
                    <button
                      onClick={() => handleUndeploy(flow.id)}
                      className="px-3 py-1 text-xs bg-red-50 text-red-600 rounded hover:bg-red-100"
                    >
                      ⏹ Stop
                    </button>
                  ) : (
                    <button
                      onClick={() => handleDeploy(flow.id)}
                      className="px-3 py-1 text-xs bg-green-50 text-green-600 rounded hover:bg-green-100"
                    >
                      ▶ Deploy
                    </button>
                  )}

                  <button
                    onClick={() => handleDelete(flow.id)}
                    className="px-3 py-1 text-xs bg-red-50 text-red-600 rounded hover:bg-red-100 ml-auto"
                  >
                    🗑
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles = {
    RUNNING: 'bg-green-100 text-green-700',
    STOPPED: 'bg-gray-100 text-gray-600',
    ERROR: 'bg-red-100 text-red-700',
  };

  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${styles[status] || styles.STOPPED}`}>
      {status === 'RUNNING' && '●'} {status}
    </span>
  );
}
```

## Step 2: Add loadFromJson to Store

```ts
// In flowStore.ts, add:
loadFromJson: (definition: FlowDefinition) => void;

// Implementation:
loadFromJson: (definition) => {
  const nodes = definition.nodes.map(n => ({
    id: n.id,
    type: n.type,
    position: n.position,
    data: {
      label: NODE_CATALOG.find(c => c.type === n.type)?.label ?? n.type,
      icon: NODE_CATALOG.find(c => c.type === n.type)?.icon ?? '❓',
      category: n.category,
      config: n.config,
    },
  }));

  const edges = definition.edges.map(e => ({
    id: e.id,
    source: e.source,
    target: e.target,
    type: 'flow',
  }));

  set({ nodes, edges, selectedNodeId: null });
},
```

## Step 3: Updated Toolbar

**src/components/Toolbar.tsx:**
```tsx
import { useState } from 'react';
import { useFlowStore } from '../store/flowStore';
import { saveFlow, deployFlow } from '../api/client';
import { FlowList } from './FlowList';

export function Toolbar() {
  const [flowListOpen, setFlowListOpen] = useState(false);
  const [flowName, setFlowName] = useState('Untitled Flow');
  const [flowId, setFlowId] = useState<string>(`flow-${Date.now()}`);
  const [status, setStatus] = useState<string | null>(null);

  const getFlowJson = useFlowStore(s => s.getFlowJson);
  const nodes = useFlowStore(s => s.nodes);

  const handleSave = async () => {
    const flow = getFlowJson();
    const result = await saveFlow({ id: flowId, name: flowName, ...flow });
    setFlowId(result.id);
    setStatus('Saved ✓');
    setTimeout(() => setStatus(null), 2000);
  };

  const handleDeploy = async () => {
    // Save first, then deploy
    await handleSave();
    const result = await deployFlow(flowId);
    setStatus(result.status === 'RUNNING' ? 'Deployed ✓' : `Error: ${result.error}`);
    setTimeout(() => setStatus(null), 3000);
  };

  return (
    <>
      <div className="h-14 border-b border-gray-200 bg-white px-4 flex items-center gap-4">
        <h1 className="text-lg font-bold text-gray-800">FlowCraft</h1>

        <div className="h-6 w-px bg-gray-200" />

        {/* Flow name */}
        <input
          value={flowName}
          onChange={e => setFlowName(e.target.value)}
          className="px-2 py-1 border border-transparent hover:border-gray-300
            focus:border-blue-400 rounded text-sm outline-none"
          placeholder="Flow name..."
        />

        <div className="flex-1" />

        {/* Status indicator */}
        {status && (
          <span className="text-sm text-green-600 animate-pulse">{status}</span>
        )}

        {/* Actions */}
        <button
          onClick={() => setFlowListOpen(true)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-md
            hover:bg-gray-50 transition"
        >
          📋 My Flows
        </button>

        <button
          onClick={handleSave}
          disabled={nodes.length === 0}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-md
            hover:bg-gray-50 disabled:opacity-50 transition"
        >
          💾 Save
        </button>

        <button
          onClick={handleDeploy}
          disabled={nodes.length === 0}
          className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded-md
            hover:bg-blue-700 disabled:opacity-50 transition"
        >
          🚀 Deploy
        </button>
      </div>

      <FlowList open={flowListOpen} onClose={() => setFlowListOpen(false)} />
    </>
  );
}
```

## Step 4: Test Panel (Try Your Flow)

After deploying an HTTP flow, users want to test it right from the UI:

**src/components/TestPanel.tsx:**
```tsx
import { useState } from 'react';

interface Props {
  flowId: string;
  httpPath?: string;
}

export function TestPanel({ flowId, httpPath }: Props) {
  const [body, setBody] = useState('{"message": "Hello from FlowCraft!"}');
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    if (!httpPath) return;
    setLoading(true);
    try {
      const res = await fetch(httpPath, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body,
      });
      const text = await res.text();
      setResponse(`${res.status} ${res.statusText}\n\n${text}`);
    } catch (err: any) {
      setResponse(`Error: ${err.message}`);
    }
    setLoading(false);
  };

  return (
    <div className="border-t border-gray-200 p-4">
      <h4 className="text-sm font-medium mb-2">🧪 Test Flow</h4>
      <p className="text-xs text-gray-500 mb-2">
        Endpoint: <code className="bg-gray-100 px-1 rounded">{httpPath}</code>
      </p>

      <textarea
        value={body}
        onChange={e => setBody(e.target.value)}
        rows={3}
        className="w-full px-3 py-2 border rounded-md text-sm font-mono mb-2"
        placeholder="Request body..."
      />

      <button
        onClick={handleTest}
        disabled={loading}
        className="w-full px-3 py-2 bg-green-600 text-white text-sm rounded-md
          hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? 'Sending...' : '▶ Send Request'}
      </button>

      {response && (
        <pre className="mt-3 p-3 bg-gray-900 text-green-400 text-xs rounded-md
          overflow-x-auto max-h-40">
          {response}
        </pre>
      )}
    </div>
  );
}
```

## The Complete User Journey

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BUILD                                                     │
│    Drag blocks → Connect → Configure each node              │
├─────────────────────────────────────────────────────────────┤
│ 2. SAVE                                                      │
│    Click 💾 → Flow stored in PostgreSQL                     │
├─────────────────────────────────────────────────────────────┤
│ 3. DEPLOY                                                    │
│    Click 🚀 → Backend compiles → Flow goes live             │
├─────────────────────────────────────────────────────────────┤
│ 4. TEST                                                      │
│    Send test request → See response in UI                   │
├─────────────────────────────────────────────────────────────┤
│ 5. ITERATE                                                   │
│    Edit flow → Save → Deploy again (hot-reload)             │
└─────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **Save ≠ Deploy** — users can draft without going live
2. **The flow list** gives users a dashboard of all their integrations
3. **Status badges** (RUNNING/STOPPED/ERROR) give instant visibility
4. **Test panel** lets users verify without leaving the app
5. **Hot-reload** means editing a live flow is seamless — save + deploy overwrites the running version

---

[← Chapter 8: Flow CRUD](chapter-08-flow-crud.md) | [Chapter 10: Live Monitoring →](chapter-10-monitoring.md)
