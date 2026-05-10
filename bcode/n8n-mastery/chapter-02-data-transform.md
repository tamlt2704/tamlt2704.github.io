# Chapter 2: Transforming Data — Expressions and Code Nodes

[← Chapter 1: Your First Workflow](chapter-01-first-workflow.md) | [Chapter 3: Branching Logic →](chapter-03-branching.md)

---

## The Problem

The deploy notification workflow from Chapter 1 works — when the payload is clean. But real GitHub webhook payloads aren't clean. They're 200+ lines of nested JSON with fields you don't need, fields that are null, and fields nested four levels deep.

Monday morning, the workflow fires but Slack shows:

```
🚀 *Deploy to undefined*
• Service: `undefined`
• By: undefined
• Commit: `undefined`
```

You check the webhook payload. GitHub's actual `deployment_status` event wraps everything differently than your test curl. The `creator` field is sometimes `sender`. The `sha` is truncated in one field and full in another. Some deploys have a `description` field, some don't.

Aisha from support: "Can you also add the deploy description to the Slack message? And format the timestamp so it's human-readable instead of that ISO garbage?"

You need to reshape messy, inconsistent data into clean, predictable output. That means expressions for simple transforms and the Code node for anything complex.

## Expressions: Beyond the Basics

You already know `{{ $json.field }}`. But expressions are JavaScript — you can do much more.

### String Manipulation

```javascript
{{ $json.email.split('@')[1] }}                    // "launchpad.io"
{{ $json.name.toLowerCase().replace(/ /g, '-') }}  // "alice-chen"
{{ $json.sha.substring(0, 7) }}                    // "a1b2c3d"
{{ $json.message || 'No description provided' }}   // fallback for null
```

### Date Formatting

```javascript
{{ new Date($json.created_at).toLocaleDateString('en-US', { 
  weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
}) }}
// "Mon, Jan 15, 09:32 AM"
```

### Conditional Values

```javascript
{{ $json.status === 'success' ? '✅' : '❌' }}
{{ $json.environment === 'production' ? '🚨 PROD' : '🧪 staging' }}
```

### Accessing Other Nodes

```javascript
{{ $('Webhook').item.json.body.sender.login }}
{{ $('Extract Fields').item.json.deployer }}
```

The `$('Node Name')` syntax lets you reach back to any previous node's output — not just the immediately preceding one.

## The Code Node: When Expressions Aren't Enough

Expressions work for one-liners. But when you need to:
- Loop through arrays
- Build objects conditionally
- Handle multiple fallback paths
- Do complex string parsing

You need the **Code node**.

### Adding a Code Node

1. Click "+" after your Webhook node
2. Search for "Code"
3. Select "Code" node
4. Choose "Run Once for All Items" or "Run Once for Each Item"

### Reshaping the GitHub Payload

Here's the real problem. GitHub sends different payload structures for `deployment` vs `deployment_status` events:

```javascript
// Code node — Run Once for Each Item
const payload = $input.item.json.body;

// Handle both event types
const deployer = payload.deployment?.creator?.login 
  || payload.sender?.login 
  || 'unknown';

const service = payload.repository?.name || 'unknown-service';

const sha = (payload.deployment?.sha || payload.sha || '').substring(0, 7);

const environment = payload.deployment?.environment 
  || payload.environment 
  || 'unknown';

const description = payload.deployment?.description 
  || payload.description 
  || '';

const timestamp = new Date(
  payload.deployment?.created_at || payload.created_at || Date.now()
).toLocaleString('en-US', { 
  timeZone: 'America/New_York',
  month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
});

return {
  json: {
    deployer,
    service,
    sha,
    environment,
    description,
    timestamp,
    isProduction: environment === 'production'
  }
};
```

The Code node outputs clean, predictable data regardless of which GitHub event format arrives.

## $json vs $input vs $('Node')

These three confuse everyone. Here's the rule:

| Reference | Use In | Meaning |
|---|---|---|
| `$json` | Expressions | Current item's JSON data |
| `$input.item.json` | Code node (each item) | Same as $json but in code |
| `$input.all()` | Code node (all items) | Array of all input items |
| `$('Node').item.json` | Expressions | Specific node's output |
| `$('Node').all()` | Code node | All items from a specific node |

### Code Node: Processing All Items

When you choose "Run Once for All Items," you get the full array:

```javascript
const items = $input.all();

const results = items.map(item => {
  const data = item.json;
  return {
    json: {
      name: data.name.trim(),
      email: data.email.toLowerCase(),
      domain: data.email.split('@')[1]
    }
  };
});

return results;
```

### Code Node: Processing Each Item

When you choose "Run Once for Each Item," you get one item at a time:

```javascript
const data = $input.item.json;

return {
  json: {
    name: data.name.trim(),
    email: data.email.toLowerCase(),
    domain: data.email.split('@')[1]
  }
};
```

Use "Each Item" when transforms are independent. Use "All Items" when you need to aggregate, deduplicate, or compare across items.

## The Updated Workflow

```json
{
  "name": "Deploy Notifications v2",
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
        "mode": "runOnceForEachItem",
        "jsCode": "const payload = $input.item.json.body;\nconst deployer = payload.deployment?.creator?.login || payload.sender?.login || 'unknown';\nconst service = payload.repository?.name || 'unknown-service';\nconst sha = (payload.deployment?.sha || '').substring(0, 7);\nconst environment = payload.deployment?.environment || 'unknown';\nconst description = payload.deployment?.description || '';\nreturn { json: { deployer, service, sha, environment, description } };"
      },
      "name": "Transform Payload",
      "type": "n8n-nodes-base.code",
      "position": [450, 300]
    },
    {
      "parameters": {
        "channel": "#deployments",
        "text": "={{ $json.environment === 'production' ? '🚨' : '🚀' }} *Deploy to {{ $json.environment }}*\n• Service: `{{ $json.service }}`\n• By: {{ $json.deployer }}\n• Commit: `{{ $json.sha }}`\n{{ $json.description ? '• Note: ' + $json.description : '' }}"
      },
      "name": "Slack",
      "type": "n8n-nodes-base.slack",
      "position": [650, 300]
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Transform Payload", "type": "main", "index": 0 }]] },
    "Transform Payload": { "main": [[{ "node": "Slack", "type": "main", "index": 0 }]] }
  }
}
```

## Common Patterns

### Merging Fields from Multiple Sources

```javascript
// Code node — combine webhook data with a lookup
const webhook = $('Webhook').item.json.body;
const userLookup = $('HTTP Request').item.json;

return {
  json: {
    ...webhook,
    userName: userLookup.display_name,
    userEmail: userLookup.email,
    eventType: webhook.action
  }
};
```

### Filtering Out Null/Empty Fields

```javascript
const data = $input.item.json;
const cleaned = Object.fromEntries(
  Object.entries(data).filter(([_, v]) => v != null && v !== '')
);
return { json: cleaned };
```

### Building Arrays for Batch Operations

```javascript
const items = $input.all();
const emails = items.map(item => item.json.email);
const unique = [...new Set(emails)];

return unique.map(email => ({ json: { email } }));
```

## What You Learned

- **Expressions** (`{{ }}`) handle simple transforms — string methods, ternaries, date formatting
- **Code node** handles complex logic — conditionals, loops, fallbacks, aggregation
- **$json** references the current item in expressions
- **$input.item.json** is the Code node equivalent
- **$('Node Name')** reaches back to any previous node's output
- **Run Once for Each Item** vs **Run Once for All Items** — choose based on whether items are independent
- **Defensive coding** — always handle null/undefined with `||` or `?.`

The deploy notifications now handle any GitHub payload format. Clean data, every time.

But there's a new request. Diana: "Production deploys should go to #deployments AND page the on-call engineer. Staging deploys just go to #dev. Failed deploys should create a Linear ticket."

Same trigger, different actions depending on the data. You need branching logic.

---

[← Chapter 1: Your First Workflow](chapter-01-first-workflow.md) | [Chapter 3: Branching Logic →](chapter-03-branching.md)
