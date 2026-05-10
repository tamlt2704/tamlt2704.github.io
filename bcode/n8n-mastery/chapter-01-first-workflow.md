# Chapter 1: Your First Workflow — Triggers and Nodes

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Transforming Data →](chapter-02-data-transform.md)

---

## The Problem

Every time the engineering team deploys to production, someone has to post in the #deployments Slack channel. The message includes: who deployed, what service, the commit hash, and whether it succeeded.

Currently, the last step of the deploy script is:

```bash
echo "Remember to post in #deployments!"
```

Nobody remembers. Half the deploys go unannounced. When something breaks, the first question is always "did someone deploy?" and nobody knows.

Jake from sales: "I need to know when deploys happen so I can warn customers about potential downtime."

Diana: "This is a 2-minute task that falls through the cracks 50% of the time. Automate it."

## The Plan

GitHub sends a webhook when a deployment succeeds. n8n catches the webhook, extracts the relevant info, formats a message, and posts it to Slack. No human in the loop.

```
[GitHub Webhook] → [Extract Data] → [Format Message] → [Post to Slack]
```

## Building It: Step by Step

### Step 1: Create the Workflow

1. Open n8n (http://localhost:5678)
2. Click "Add workflow" (top right)
3. Name it "Deploy Notifications"

You see a blank canvas with a single trigger node placeholder.

### Step 2: Add a Webhook Trigger

1. Click the "+" on the canvas
2. Search for "Webhook"
3. Select "Webhook" trigger

Configure it:
- **HTTP Method**: POST
- **Path**: `deploy-hook` (this creates the URL: `http://localhost:5678/webhook/deploy-hook`)
- **Authentication**: None (we'll add this in Chapter 6)

Click "Listen for test event" — n8n is now waiting for a request.

### Step 3: Test the Webhook

In a terminal, simulate a GitHub deployment event:

```bash
curl -X POST http://localhost:5678/webhook-test/deploy-hook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "completed",
    "deployment": {
      "environment": "production",
      "sha": "a1b2c3d",
      "creator": {
        "login": "alice"
      }
    },
    "repository": {
      "name": "api-service"
    }
  }'
```

n8n captures the request. You see the JSON data in the webhook node's output panel. The trigger works.

### Step 4: Add a Set Node (Extract Data)

1. Click "+" after the Webhook node
2. Search for "Edit Fields" (formerly "Set")
3. Add these fields:

| Field Name | Value (Expression) |
|---|---|
| deployer | `{{ $json.body.deployment.creator.login }}` |
| service | `{{ $json.body.repository.name }}` |
| sha | `{{ $json.body.deployment.sha }}` |
| environment | `{{ $json.body.deployment.environment }}` |

This extracts only what we need from the verbose GitHub payload.

### Step 5: Add a Slack Node

1. Click "+" after the Set node
2. Search for "Slack"
3. Select "Send a Message"

Configure:
- **Credential**: Connect your Slack workspace (OAuth2 — n8n walks you through it)
- **Channel**: `#deployments`
- **Message**:

```
🚀 *Deploy to {{ $json.environment }}*
• Service: `{{ $json.service }}`
• By: {{ $json.deployer }}
• Commit: `{{ $json.sha }}`
```

### Step 6: Activate

Click "Save" then toggle the workflow to "Active" (top right switch).

Now every POST to your webhook URL triggers the full flow. Connect GitHub's deployment webhook to this URL, and deploys announce themselves.

## The Complete Workflow (JSON Export)

n8n workflows are JSON. You can import this directly:

```json
{
  "name": "Deploy Notifications",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "deploy-hook",
        "responseMode": "onReceived"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            { "name": "deployer", "value": "={{ $json.body.deployment.creator.login }}" },
            { "name": "service", "value": "={{ $json.body.repository.name }}" },
            { "name": "sha", "value": "={{ $json.body.deployment.sha }}" },
            { "name": "environment", "value": "={{ $json.body.deployment.environment }}" }
          ]
        }
      },
      "name": "Extract Fields",
      "type": "n8n-nodes-base.set",
      "position": [450, 300]
    },
    {
      "parameters": {
        "channel": "#deployments",
        "text": "🚀 *Deploy to {{ $json.environment }}*\n• Service: `{{ $json.service }}`\n• By: {{ $json.deployer }}\n• Commit: `{{ $json.sha }}`"
      },
      "name": "Slack",
      "type": "n8n-nodes-base.slack",
      "position": [650, 300]
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Extract Fields", "type": "main", "index": 0 }]] },
    "Extract Fields": { "main": [[{ "node": "Slack", "type": "main", "index": 0 }]] }
  }
}
```

## Understanding Data Flow

Let's trace the data through each node:

**Webhook output:**
```json
{
  "headers": { "content-type": "application/json" },
  "body": {
    "action": "completed",
    "deployment": {
      "environment": "production",
      "sha": "a1b2c3d",
      "creator": { "login": "alice" }
    },
    "repository": { "name": "api-service" }
  }
}
```

**Extract Fields output:**
```json
{
  "deployer": "alice",
  "service": "api-service",
  "sha": "a1b2c3d",
  "environment": "production"
}
```

**Slack output:**
```json
{
  "ok": true,
  "channel": "C01234567",
  "ts": "1234567890.123456"
}
```

Each node transforms the data and passes it forward. The Slack node receives the clean, extracted fields — not the raw GitHub payload.

## Expressions: The Glue

n8n expressions use double curly braces: `{{ }}`. Inside, you can access:

| Expression | Meaning |
|---|---|
| `{{ $json.field }}` | Current item's data |
| `{{ $json.nested.field }}` | Nested access |
| `{{ $('Node Name').item.json.field }}` | Data from a specific previous node |
| `{{ $now }}` | Current timestamp |
| `{{ $execution.id }}` | Current execution ID |

Expressions are JavaScript under the hood. You can use methods:

```
{{ $json.email.split('@')[1] }}          → "example.com"
{{ $json.name.toUpperCase() }}           → "ALICE"
{{ $json.amount > 100 ? 'high' : 'low' }} → "high"
```

## Common Mistakes

### Forgetting the `body` wrapper

Webhook data arrives inside `$json.body`, not directly in `$json`:

```
WRONG: {{ $json.deployment.sha }}
RIGHT: {{ $json.body.deployment.sha }}
```

### Test mode vs. Production mode

The test webhook URL is different from the production URL:
- Test: `http://localhost:5678/webhook-test/deploy-hook`
- Production: `http://localhost:5678/webhook/deploy-hook`

Test mode only works when you click "Listen for test event." Production mode works when the workflow is active.

### Not activating the workflow

Building and testing a workflow doesn't activate it. You must toggle the "Active" switch. Inactive workflows don't respond to triggers.

## What You Learned

- **Triggers** start workflows (webhook, schedule, event)
- **Nodes** process data (extract, transform, send)
- **Connections** pass data between nodes
- **Expressions** reference data with `{{ $json.field }}`
- **Data flow** — each node receives, transforms, and passes forward
- **Test vs. Production** — different URLs, different activation states

The deploy notifications work. Jake gets his alerts. Diana is happy.

Then Monday morning: the webhook fires but Slack returns a 429 (rate limited). The message never posts. Nobody notices until Wednesday.

Diana: "If the automation fails, it's worse than doing it manually. At least manually, someone knows it didn't happen."

She's right. We need error handling. But first — the data coming from GitHub is messier than our test payload. We need to transform it properly.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Transforming Data →](chapter-02-data-transform.md)
