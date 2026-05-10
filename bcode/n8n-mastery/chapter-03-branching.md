# Chapter 3: Branching Logic — Conditional Routing

[← Chapter 2: Transforming Data](chapter-02-data-transform.md) | [Chapter 4: Loops and Batches →](chapter-04-loops.md)

---

## The Problem

The deploy notification workflow posts every event to #deployments. But not all deploy events are equal:

- **Production success** → notify #deployments + page on-call
- **Staging success** → notify #dev only
- **Any failure** → create a Linear ticket + alert #incidents
- **Rollback** → notify #deployments + #incidents + page on-call

Right now, a staging deploy to a test branch triggers the same alert as a production rollback. Jake from sales got paged at 2 AM because someone deployed a typo fix to staging.

Diana: "Route the alerts properly. Production failures are emergencies. Staging successes are informational. Stop waking people up for nothing."

## The IF Node: Binary Decisions

The simplest branch: true or false.

### Setup

1. Add an IF node after your Transform Payload node
2. Configure the condition:

**Condition**: `{{ $json.environment }}` — **equals** — `production`

The IF node has two outputs:
- **true** (top) → items where the condition matched
- **false** (bottom) → everything else

```
[Transform] → [IF: is production?]
                  ├── true  → [Slack #deployments] → [Page On-Call]
                  └── false → [Slack #dev]
```

### Multiple Conditions

You can add multiple conditions with AND/OR logic:

```
Condition 1: {{ $json.environment }} equals "production"
AND
Condition 2: {{ $json.status }} equals "failure"
```

This routes only production failures to the true branch.

## The Switch Node: Multiple Paths

When you have more than two outcomes, use the Switch node. It's like a `switch` statement — route items to different outputs based on a value.

### Setup

1. Add a Switch node after Transform Payload
2. Set **Mode** to "Rules"
3. Add routing rules:

| Rule | Condition | Output |
|---|---|---|
| 0 | `{{ $json.environment }}` equals `production` AND `{{ $json.status }}` equals `success` | Output 0 |
| 1 | `{{ $json.environment }}` equals `production` AND `{{ $json.status }}` equals `failure` | Output 1 |
| 2 | `{{ $json.action }}` equals `rollback` | Output 2 |
| 3 | Fallback (no match) | Output 3 |

Each output connects to a different downstream path:

```
                    ┌── Output 0 → [Slack #deployments] → [Page On-Call]
[Transform] → [Switch]── Output 1 → [Linear Ticket] → [Slack #incidents]
                    ├── Output 2 → [Slack #deployments] → [Slack #incidents] → [Page On-Call]
                    └── Fallback  → [Slack #dev]
```

### Switch by Value

For simpler cases, set Mode to "Expression" and route by a single field's value:

**Routing value**: `{{ $json.environment }}`

| Value | Output |
|---|---|
| `production` | Output 0 |
| `staging` | Output 1 |
| `development` | Output 2 |

This is cleaner when you're routing purely on one field.

## The Complete Branching Workflow

```json
{
  "name": "Deploy Notifications v3 — Branching",
  "nodes": [
    {
      "parameters": { "httpMethod": "POST", "path": "deploy-hook" },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "const p = $input.item.json.body;\nreturn { json: { deployer: p.sender?.login || 'unknown', service: p.repository?.name, sha: (p.deployment?.sha || '').substring(0,7), environment: p.deployment?.environment || 'unknown', status: p.deployment_status?.state || p.action || 'unknown', action: p.action } };"
      },
      "name": "Transform",
      "type": "n8n-nodes-base.code",
      "position": [450, 300]
    },
    {
      "parameters": {
        "rules": {
          "rules": [
            { "conditions": { "conditions": [{ "leftValue": "={{ $json.action }}", "rightValue": "rollback" }] }, "output": 0 },
            { "conditions": { "conditions": [{ "leftValue": "={{ $json.environment }}", "rightValue": "production" }, { "leftValue": "={{ $json.status }}", "rightValue": "failure" }] }, "output": 1 },
            { "conditions": { "conditions": [{ "leftValue": "={{ $json.environment }}", "rightValue": "production" }, { "leftValue": "={{ $json.status }}", "rightValue": "success" }] }, "output": 2 }
          ],
          "fallbackOutput": 3
        }
      },
      "name": "Route by Event",
      "type": "n8n-nodes-base.switch",
      "position": [650, 300]
    },
    {
      "parameters": { "channel": "#incidents", "text": "🔄 *ROLLBACK* on `{{ $json.service }}` by {{ $json.deployer }}" },
      "name": "Alert Rollback",
      "type": "n8n-nodes-base.slack",
      "position": [900, 150]
    },
    {
      "parameters": { "channel": "#incidents", "text": "❌ *DEPLOY FAILED* — `{{ $json.service }}` ({{ $json.environment }}) by {{ $json.deployer }}" },
      "name": "Alert Failure",
      "type": "n8n-nodes-base.slack",
      "position": [900, 300]
    },
    {
      "parameters": { "channel": "#deployments", "text": "✅ `{{ $json.service }}` deployed to production by {{ $json.deployer }} ({{ $json.sha }})" },
      "name": "Notify Success",
      "type": "n8n-nodes-base.slack",
      "position": [900, 450]
    },
    {
      "parameters": { "channel": "#dev", "text": "🧪 `{{ $json.service }}` deployed to {{ $json.environment }} by {{ $json.deployer }}" },
      "name": "Notify Dev",
      "type": "n8n-nodes-base.slack",
      "position": [900, 600]
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Transform", "type": "main", "index": 0 }]] },
    "Transform": { "main": [[{ "node": "Route by Event", "type": "main", "index": 0 }]] },
    "Route by Event": {
      "main": [
        [{ "node": "Alert Rollback", "type": "main", "index": 0 }],
        [{ "node": "Alert Failure", "type": "main", "index": 0 }],
        [{ "node": "Notify Success", "type": "main", "index": 0 }],
        [{ "node": "Notify Dev", "type": "main", "index": 0 }]
      ]
    }
  }
}
```

## Patterns and Tips

### Combining IF Nodes in Sequence

Sometimes you need nested logic. Chain IF nodes:

```
[IF: is production?]
    ├── true → [IF: is failure?]
    │              ├── true  → [Create Ticket + Alert]
    │              └── false → [Notify Success]
    └── false → [Notify Dev]
```

This works but gets messy fast. Prefer a single Switch node with compound conditions.

### The "No Match" Trap

If no Switch rule matches and you don't configure a fallback output, the item is **silently dropped**. Always set a fallback — even if it just logs the unmatched item.

### Routing Multiple Items

If your workflow processes 10 items, the Switch node evaluates each one independently. 3 might go to Output 0, 5 to Output 1, and 2 to the fallback. Each downstream path receives only its matched items.

### Using Expressions in Conditions

Conditions support expressions for dynamic comparisons:

```
Left:  {{ $json.amount }}
Op:    greater than
Right: {{ $('Config').item.json.alertThreshold }}
```

This lets you externalize thresholds without editing the workflow.

## Debugging Branches

When a branch doesn't fire as expected:

1. **Check the Switch node's input** — click the node and inspect what data it received
2. **Check data types** — `"100"` (string) ≠ `100` (number). Use `{{ Number($json.amount) }}` to coerce
3. **Check rule order** — rules are evaluated top to bottom, first match wins
4. **Check the fallback** — if items end up in fallback unexpectedly, your conditions don't match

## What You Learned

- **IF node** splits items into two paths (true/false)
- **Switch node** routes items to multiple outputs based on rules
- **Rules mode** supports compound conditions (AND/OR)
- **Expression mode** routes by a single field's value
- **Fallback output** catches items that match no rule — always configure it
- **Each item is evaluated independently** — different items can take different paths
- **Rule order matters** — first match wins

Jake no longer gets paged for staging deploys. Production failures create tickets automatically. Rollbacks trigger the full incident response.

Next problem: Jake wants all 500 HubSpot contacts synced to Notion. "Just loop through them," he says. You try. HubSpot's API returns 429 after 40 requests. The workflow crashes halfway through, leaving 40 contacts synced and 460 orphaned.

You need to process data in batches.

---

[← Chapter 2: Transforming Data](chapter-02-data-transform.md) | [Chapter 4: Loops and Batches →](chapter-04-loops.md)
