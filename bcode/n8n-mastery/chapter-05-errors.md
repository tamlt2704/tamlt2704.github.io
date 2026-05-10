# Chapter 5: Error Handling — When Workflows Fail

[← Chapter 4: Loops and Batches](chapter-04-loops.md) | [Chapter 6: Webhooks →](chapter-06-webhooks.md)

---

## The Problem

Thursday, 3:17 AM. The Slack API returns HTTP 429 — rate limited. The deploy notification workflow fails. No alert is sent. No error is logged anywhere you'd notice. The workflow just... stops.

You find out on Monday when Diana asks: "Did anyone deploy over the weekend?" Three deploys happened. Zero notifications. The workflow failed on the first one and stayed broken for the rest.

Diana: "If the automation fails silently, it's worse than not having automation at all. At least when humans forget, they eventually remember. A broken workflow never remembers."

She's right. Every workflow needs three things:
1. **Retry** — try again before giving up
2. **Alert** — tell someone it failed
3. **Recover** — don't lose the data

## Retry on Failure: Node-Level

Every node has retry settings. Click any node → Settings:

- **Retry On Fail**: Enable
- **Max Tries**: `3`
- **Wait Between Tries**: `1000` ms (increases exponentially)

For the Slack node:
```
Max Tries: 3
Wait Between Tries: 2000ms
```

n8n will retry the node up to 3 times with increasing delays (2s, 4s, 8s). If Slack returns 429, the retry usually succeeds after the rate limit window resets.

### When to Retry

| Error Type | Retry? | Why |
|---|---|---|
| 429 Rate Limited | Yes | Temporary, resolves with time |
| 500 Server Error | Yes | Might be a transient issue |
| 503 Unavailable | Yes | Service might be restarting |
| 400 Bad Request | No | Your data is wrong, retrying won't help |
| 401 Unauthorized | No | Credentials are invalid |
| 404 Not Found | No | Resource doesn't exist |

## The Error Trigger Workflow

Node-level retries handle transient failures. But what about when a workflow truly fails — all retries exhausted, unrecoverable error?

n8n has a special trigger: **Error Trigger**. It fires whenever *any* workflow in your instance fails.

### Create an Error Handler Workflow

1. Create a new workflow: "Error Handler — Alert on Failure"
2. Add an **Error Trigger** node (search for "Error Trigger")
3. Connect it to a Slack node

The Error Trigger receives:

```json
{
  "execution": {
    "id": "12345",
    "url": "http://localhost:5678/execution/12345",
    "error": {
      "message": "Request failed with status code 429",
      "node": "Slack"
    },
    "lastNodeExecuted": "Slack",
    "mode": "trigger"
  },
  "workflow": {
    "id": "1",
    "name": "Deploy Notifications"
  }
}
```

### The Alert Message

```
❌ *Workflow Failed*
• Workflow: {{ $json.workflow.name }}
• Node: {{ $json.execution.lastNodeExecuted }}
• Error: {{ $json.execution.error.message }}
• Execution: {{ $json.execution.url }}
```

### Setting It as the Global Error Workflow

1. Go to Settings → Workflow Settings (on any workflow)
2. Set "Error Workflow" to your Error Handler workflow

Or set it instance-wide in n8n settings so every workflow uses it by default.

## The Dead Letter Pattern

When a workflow fails, the data that triggered it is lost — unless you save it. The "dead letter" pattern captures failed items for later reprocessing.

### Implementation

```json
{
  "name": "Error Handler with Dead Letter",
  "nodes": [
    {
      "parameters": {},
      "name": "Error Trigger",
      "type": "n8n-nodes-base.errorTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "const error = $input.item.json;\nreturn {\n  json: {\n    workflow_name: error.workflow.name,\n    workflow_id: error.workflow.id,\n    error_message: error.execution.error.message,\n    failed_node: error.execution.lastNodeExecuted,\n    execution_id: error.execution.id,\n    execution_url: error.execution.url,\n    timestamp: new Date().toISOString(),\n    status: 'failed'\n  }\n};"
      },
      "name": "Format Error",
      "type": "n8n-nodes-base.code",
      "position": [450, 300]
    },
    {
      "parameters": {
        "operation": "insert",
        "table": "dead_letters",
        "columns": "workflow_name,workflow_id,error_message,failed_node,execution_id,execution_url,timestamp,status"
      },
      "name": "Save to Postgres",
      "type": "n8n-nodes-base.postgres",
      "position": [650, 300]
    },
    {
      "parameters": {
        "channel": "#ops-alerts",
        "text": "❌ *{{ $json.workflow_name }}* failed at node `{{ $json.failed_node }}`\nError: {{ $json.error_message }}\n<{{ $json.execution_url }}|View Execution>"
      },
      "name": "Alert Slack",
      "type": "n8n-nodes-base.slack",
      "position": [650, 150]
    }
  ],
  "connections": {
    "Error Trigger": { "main": [[{ "node": "Format Error", "type": "main", "index": 0 }]] },
    "Format Error": { "main": [[{ "node": "Save to Postgres", "type": "main", "index": 0 }, { "node": "Alert Slack", "type": "main", "index": 0 }]] }
  }
}
```

### The Dead Letter Table

```sql
CREATE TABLE dead_letters (
  id SERIAL PRIMARY KEY,
  workflow_name TEXT NOT NULL,
  workflow_id TEXT NOT NULL,
  error_message TEXT,
  failed_node TEXT,
  execution_id TEXT,
  execution_url TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'failed',  -- failed, retried, resolved
  resolved_at TIMESTAMPTZ
);
```

Now you can query failed executions, retry them manually, or build a reprocessing workflow.

## Continue On Fail: Graceful Degradation

Sometimes you don't want the entire workflow to stop because one node fails. The **Continue On Fail** setting lets a node fail without killing the workflow.

### Use Case: Batch Processing

In the HubSpot sync (Chapter 4), if one contact fails to create in Notion, you don't want to abort the other 499.

1. Click the Notion node → Settings
2. Enable "Continue On Fail"
3. Failed items continue through the workflow with an `error` field

After the batch, add an IF node:

```
[Create Notion Page (Continue On Fail)] → [IF: has error?]
    ├── true  → [Log Failed Items]
    └── false → [Continue normally]
```

Condition: `{{ $json.error }}` — **is not empty**

## Pattern: Circuit Breaker

If an API is consistently failing, don't keep hammering it. Implement a circuit breaker:

```javascript
// Code node — check failure count before proceeding
const recentFailures = $('Check Dead Letters').all();
const failureCount = recentFailures.filter(
  f => f.json.workflow_name === 'HubSpot Sync' 
    && new Date(f.json.timestamp) > new Date(Date.now() - 3600000) // last hour
).length;

if (failureCount >= 5) {
  throw new Error('Circuit breaker open: HubSpot Sync has failed 5+ times in the last hour. Manual intervention required.');
}

return $input.all();
```

## Pattern: Retry with Backoff (Workflow-Level)

For workflow-level retries (not just node-level), use a separate "retry" workflow:

```
[Schedule: Every 5 min] → [Query Dead Letters where status='failed'] → [IF: any results?]
    ├── true  → [Re-trigger original workflow] → [Mark as 'retried']
    └── false → [Do nothing]
```

This gives you automatic retry with configurable intervals, without blocking the original workflow.

## What You Learned

- **Node-level retry** handles transient failures (429, 500, 503)
- **Error Trigger workflow** catches failures across all workflows
- **Dead letter pattern** saves failed data for reprocessing
- **Continue On Fail** prevents one bad item from killing a batch
- **Circuit breaker** stops hammering a broken API
- **Workflow-level retry** reprocesses dead letters on a schedule
- **Always alert** — a failed workflow that nobody knows about is worse than no automation

The deploy notifications now retry 3 times on rate limits, alert #ops-alerts on failure, and save failed executions for reprocessing. Diana sleeps better.

Next: Stripe needs to tell you when a payment succeeds. GitHub needs to tell you when a PR is merged. External services need to push data *into* your workflows. You need proper webhooks.

---

[← Chapter 4: Loops and Batches](chapter-04-loops.md) | [Chapter 6: Webhooks →](chapter-06-webhooks.md)
