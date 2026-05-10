# Chapter 10: Sub-Workflows — Modularity

[← Chapter 9: Scheduling](chapter-09-scheduling.md) | [Chapter 11: AI Nodes →](chapter-11-ai-nodes.md)

---

## The Problem

You have 12 workflows. Eight of them end with "send a Slack notification." Each one has:
- A Slack node configured with credentials
- A Code node that formats the message
- Error handling (retry on 429)
- A fallback that logs to Postgres if Slack is down

That's 4 nodes × 8 workflows = 32 nodes doing the same thing. When Diana asks you to add a thread reply to every notification, you have to edit 8 workflows. You miss one. That workflow sends messages without thread context for two weeks before anyone notices.

Diana: "This is the same problem we had with manual processes — duplication. Except now the duplication is in the automation itself."

You need reusable components. In code, you'd write a function. In n8n, you use sub-workflows.

## Execute Workflow Node

The **Execute Workflow** node calls another workflow like a function call. You pass data in, it processes, and returns data back.

### The Pattern

**Parent workflow:**
```
[Trigger] → [Business Logic] → [Execute Workflow: Send Notification] → [Continue]
```

**Child workflow (sub-workflow):**
```
[Execute Workflow Trigger] → [Format Message] → [Send Slack] → [Handle Errors] → [Return Data]
```

The parent passes data to the child. The child does its work and returns a result. The parent continues with the returned data.

## Building the Reusable Notification Workflow

### Step 1: Create the Sub-Workflow

Create a new workflow: "Shared: Send Slack Notification"

```json
{
  "name": "Shared: Send Slack Notification",
  "nodes": [
    {
      "parameters": {},
      "name": "Execute Workflow Trigger",
      "type": "n8n-nodes-base.executeWorkflowTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "const input = $input.item.json;\nconst emoji = input.level === 'error' ? '❌' : input.level === 'warning' ? '⚠️' : 'ℹ️';\nconst header = input.title || 'Notification';\nconst body = input.message || '';\nconst footer = input.source ? `_from ${input.source}_` : '';\n\nreturn { json: { channel: input.channel || '#ops', text: `${emoji} *${header}*\\n${body}\\n${footer}`, thread_ts: input.thread_ts || undefined } };"
      },
      "name": "Format Message",
      "type": "n8n-nodes-base.code",
      "position": [450, 300]
    },
    {
      "parameters": {
        "channel": "={{ $json.channel }}",
        "text": "={{ $json.text }}",
        "otherOptions": { "thread_ts": "={{ $json.thread_ts }}" }
      },
      "name": "Send Slack",
      "type": "n8n-nodes-base.slack",
      "position": [650, 300],
      "retryOnFail": true,
      "maxTries": 3,
      "waitBetweenTries": 2000
    }
  ],
  "connections": {
    "Execute Workflow Trigger": { "main": [[{ "node": "Format Message", "type": "main", "index": 0 }]] },
    "Format Message": { "main": [[{ "node": "Send Slack", "type": "main", "index": 0 }]] }
  }
}
```

### Step 2: Call It from Parent Workflows

In any parent workflow, add an Execute Workflow node:

```json
{
  "parameters": {
    "workflowId": "={{ 'shared-slack-notification' }}",
    "workflowInputs": {
      "values": [
        { "name": "channel", "value": "#deployments" },
        { "name": "title", "value": "Deploy Complete" },
        { "name": "message", "value": "={{ `Service: ${$json.service}\\nBy: ${$json.deployer}\\nCommit: ${$json.sha}` }}" },
        { "name": "level", "value": "info" },
        { "name": "source", "value": "Deploy Notifications" }
      ]
    }
  },
  "name": "Send Notification",
  "type": "n8n-nodes-base.executeWorkflow",
  "position": [650, 300]
}
```

### The Interface Contract

The sub-workflow expects this input shape:

| Field | Required | Description |
|---|---|---|
| `channel` | No | Slack channel (default: #ops) |
| `title` | No | Bold header text |
| `message` | Yes | Message body |
| `level` | No | `info`, `warning`, or `error` (affects emoji) |
| `source` | No | Which workflow sent this |
| `thread_ts` | No | Reply in thread |

Any workflow can call this with just a `message` and get sensible defaults for everything else.

## Passing Data Back

Sub-workflows can return data to the parent. The last node's output becomes the return value.

### Sub-workflow returns success/failure:

```javascript
// Last Code node in sub-workflow
const slackResponse = $('Send Slack').item.json;

return {
  json: {
    success: slackResponse.ok === true,
    messageTs: slackResponse.ts,
    channel: slackResponse.channel
  }
};
```

### Parent uses the return value:

```javascript
// After Execute Workflow node in parent
const result = $json; // This is the sub-workflow's return value

if (!result.success) {
  // Slack failed even after retries — log to dead letter
}

// Use messageTs for thread replies later
const threadTs = result.messageTs;
```

## Error Propagation

By default, if a sub-workflow fails, the error propagates to the parent — the parent workflow also fails. This is usually what you want.

### Handling Sub-Workflow Errors in the Parent

Enable **Continue On Fail** on the Execute Workflow node to catch sub-workflow errors without killing the parent:

```
[Business Logic] → [Execute Workflow (Continue On Fail)] → [IF: error?]
    ├── true  → [Fallback: Log to DB]
    └── false → [Continue normally]
```

### When to Propagate vs. Handle

| Scenario | Strategy |
|---|---|
| Notification failed | Handle in parent (non-critical) |
| Data sync failed | Propagate (critical — parent should fail too) |
| Enrichment lookup failed | Handle (use defaults, continue) |
| Payment processing failed | Propagate (must not continue) |

## More Reusable Sub-Workflows

### "Shared: Lookup Customer"

```
Input: { email } or { stripe_id }
Output: { customer } or { found: false }
```

Used by: payment workflows, support workflows, reporting workflows.

### "Shared: Create Linear Ticket"

```
Input: { title, description, priority, team }
Output: { ticket_id, ticket_url }
```

Used by: error handler, support escalation, deploy failures.

### "Shared: Log to Audit Trail"

```
Input: { action, actor, resource, details }
Output: { logged: true }
```

Used by: every workflow that modifies data.

## Naming Conventions

Prefix sub-workflows so they're easy to identify:

| Prefix | Meaning |
|---|---|
| `Shared:` | Reusable sub-workflow |
| `Handler:` | Error handler |
| `Report:` | Scheduled report |
| `Sync:` | Data synchronization |
| `Monitor:` | Health check / monitoring |

## Avoiding Infinite Loops

A sub-workflow can call another sub-workflow. But if Workflow A calls Workflow B which calls Workflow A — infinite loop. n8n will eventually kill it, but not before consuming resources.

Rules:
1. Sub-workflows should never call their parent
2. Keep the call depth shallow (max 2-3 levels)
3. Never use Execute Workflow with dynamic workflow IDs from untrusted input

## Performance Considerations

Each Execute Workflow call has overhead — starting a new execution context, passing data, returning results. For high-throughput scenarios:

- Don't call a sub-workflow inside a loop of 1,000 items
- Instead, pass all 1,000 items to the sub-workflow at once and let it batch internally
- Sub-workflows are for modularity, not for per-item processing

## What You Learned

- **Execute Workflow node** calls another workflow like a function
- **Execute Workflow Trigger** is the entry point for sub-workflows
- **Data passes in** via workflow inputs and **returns** via the last node's output
- **Error propagation** — sub-workflow failures bubble up to the parent by default
- **Continue On Fail** catches sub-workflow errors without killing the parent
- **Naming conventions** (`Shared:`, `Handler:`) keep workflows organized
- **Avoid infinite loops** — never let sub-workflows call their parents
- **Batch, don't loop** — pass arrays to sub-workflows instead of calling per-item

The Slack notification logic now lives in one place. Change the format once, all 12 workflows get the update. Diana's thread reply request? One edit, done everywhere.

Next: Aisha's support team is drowning in tickets. "Can the automation figure out if a ticket is a bug report, a feature request, or just a question? I spend 20 minutes every morning just categorizing." You need intelligence — not just logic.

---

[← Chapter 9: Scheduling](chapter-09-scheduling.md) | [Chapter 11: AI Nodes →](chapter-11-ai-nodes.md)
