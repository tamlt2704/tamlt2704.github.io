# Chapter 8: API Integrations — Connecting Anything

[← Chapter 7: Database Operations](chapter-07-databases.md) | [Chapter 9: Scheduling →](chapter-09-scheduling.md)

---

## The Problem

LaunchPad uses an internal tool called **FlagSmith** for feature flags. The engineering team toggles flags through its API. The product team wants to know when flags change — specifically when a flag is enabled for a customer segment.

FlagSmith has a REST API. It does not have an n8n integration. There's no pre-built node for it.

Dev team: "Just use the API. Here's the docs. It's standard REST with OAuth2."

You: "Cool. I'll use the HTTP Request node."

This is the reality of automation: most tools you need to connect don't have native n8n nodes. The HTTP Request node is your universal adapter.

## HTTP Request Node: The Universal Connector

The HTTP Request node makes arbitrary HTTP calls. If a service has an API, you can connect to it.

### Basic GET Request

```json
{
  "parameters": {
    "method": "GET",
    "url": "https://api.flagsmith.internal/v1/flags",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "options": {
      "response": { "response": { "responseFormat": "json" } }
    }
  },
  "name": "Get Feature Flags",
  "type": "n8n-nodes-base.httpRequest",
  "position": [450, 300]
}
```

### POST with JSON Body

```json
{
  "parameters": {
    "method": "POST",
    "url": "https://api.flagsmith.internal/v1/flags",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        { "name": "flag_name", "value": "={{ $json.flag }}" },
        { "name": "enabled", "value": "={{ $json.enabled }}" },
        { "name": "segment", "value": "={{ $json.segment }}" }
      ]
    }
  },
  "name": "Update Flag",
  "type": "n8n-nodes-base.httpRequest",
  "position": [450, 300]
}
```

## OAuth2 Credentials

Most production APIs use OAuth2. n8n handles the token refresh automatically — you configure it once.

### Setting Up OAuth2 Credentials

1. Go to Credentials → Add Credential → "OAuth2 API"
2. Configure:

| Field | Value |
|---|---|
| Grant Type | Client Credentials (for service-to-service) |
| Access Token URL | `https://auth.flagsmith.internal/oauth/token` |
| Client ID | Your app's client ID |
| Client Secret | Your app's client secret |
| Scope | `flags:read flags:write` |
| Authentication | Send in Body |

3. Test → Save

Now any HTTP Request node using this credential automatically:
- Requests a token before the first call
- Includes the token in the Authorization header
- Refreshes the token when it expires

### Using the Credential

In the HTTP Request node:
- **Authentication**: "Predefined Credential Type"
- **Credential Type**: "OAuth2 API"
- **Credential**: Select your saved credential

No manual token management. No expired token errors at 3 AM.

## Pagination: Getting All Results

APIs return paginated results. FlagSmith returns 50 flags per page. You have 200 flags. You need all of them.

### Built-in Pagination

The HTTP Request node has pagination support:

1. Enable **Pagination** in the node options
2. Configure:

**Pagination Type**: Response Contains Next URL

```
Next URL: {{ $response.body.next_page_url }}
Max Pages: 10
```

Or for offset-based pagination:

**Pagination Type**: Update a Parameter in Each Request

```
Parameter Name: offset
Parameter Type: Query
Initial Value: 0
Increment By: {{ $response.body.results.length }}
Complete When: {{ $response.body.results.length === 0 }}
```

n8n automatically loops through pages and combines all results into a single output array.

### Manual Pagination (Code Node)

For complex pagination logic:

```javascript
// Code node — manual pagination
const allResults = [];
let page = 1;
let hasMore = true;

while (hasMore) {
  const response = await this.helpers.httpRequest({
    method: 'GET',
    url: 'https://api.flagsmith.internal/v1/flags',
    qs: { page, per_page: 50 },
    headers: { Authorization: `Bearer ${$credentials.oAuth2Api.accessToken}` }
  });
  
  allResults.push(...response.results);
  hasMore = response.has_more;
  page++;
  
  if (page > 20) break; // Safety limit
}

return allResults.map(flag => ({ json: flag }));
```

## Error Handling for HTTP Requests

APIs fail. Handle it gracefully.

### Node Settings

- **Retry On Fail**: Yes
- **Max Tries**: 3
- **Continue On Fail**: Enable if one failure shouldn't kill the workflow

### Checking Response Status

After an HTTP Request node, check the status:

```javascript
// Code node — validate response
const response = $input.item.json;

if (response.statusCode && response.statusCode >= 400) {
  throw new Error(`API returned ${response.statusCode}: ${JSON.stringify(response.body)}`);
}

// Also handle unexpected response shapes
if (!response.results || !Array.isArray(response.results)) {
  throw new Error(`Unexpected response format: ${JSON.stringify(response).substring(0, 200)}`);
}

return $input.all();
```

### Rate Limit Handling

If the API returns 429, the retry-on-fail with backoff usually handles it. For more control:

```javascript
// Code node — check rate limit headers
const remaining = $input.item.json.headers['x-ratelimit-remaining'];
const resetAt = $input.item.json.headers['x-ratelimit-reset'];

if (parseInt(remaining) < 5) {
  const waitMs = (parseInt(resetAt) * 1000) - Date.now();
  if (waitMs > 0) {
    await new Promise(resolve => setTimeout(resolve, waitMs));
  }
}

return $input.all();
```

## The Complete Integration Workflow

Monitor FlagSmith for changes and notify Slack:

```json
{
  "name": "Feature Flag Monitor",
  "nodes": [
    {
      "parameters": { "rule": { "interval": [{ "field": "minutes", "minutesInterval": 5 }] } },
      "name": "Every 5 Minutes",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://api.flagsmith.internal/v1/flags/audit-log",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "oAuth2Api",
        "options": { "response": { "response": { "responseFormat": "json" } } },
        "queryParameters": { "parameters": [{ "name": "since", "value": "={{ new Date(Date.now() - 300000).toISOString() }}" }] }
      },
      "name": "Get Recent Changes",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": { "conditions": [{ "leftValue": "={{ $json.changes?.length }}", "rightValue": "0", "operator": { "type": "number", "operation": "gt" } }] }
      },
      "name": "Any Changes?",
      "type": "n8n-nodes-base.if",
      "position": [650, 300]
    },
    {
      "parameters": {
        "channel": "#product",
        "text": "🚩 Feature flag changed:\n{{ $json.changes.map(c => `• ${c.flag_name}: ${c.old_value} → ${c.new_value} (by ${c.changed_by})`).join('\\n') }}"
      },
      "name": "Notify Product",
      "type": "n8n-nodes-base.slack",
      "position": [850, 200]
    }
  ],
  "connections": {
    "Every 5 Minutes": { "main": [[{ "node": "Get Recent Changes", "type": "main", "index": 0 }]] },
    "Get Recent Changes": { "main": [[{ "node": "Any Changes?", "type": "main", "index": 0 }]] },
    "Any Changes?": { "main": [[{ "node": "Notify Product", "type": "main", "index": 0 }], []] }
  }
}
```

## Patterns

### API Key in Header

```
Authentication: Generic Credential Type → Header Auth
Header Name: X-API-Key
Header Value: your-api-key
```

### Bearer Token (Static)

```
Authentication: Generic Credential Type → Header Auth
Header Name: Authorization
Header Value: Bearer your-static-token
```

### Sending Form Data

Set **Content Type** to `multipart/form-data` for file uploads or form submissions.

### Following Redirects

Enable **Follow Redirects** in options. Some APIs redirect on success (302 to the created resource).

## What You Learned

- **HTTP Request node** connects to any REST API — it's the universal adapter
- **OAuth2 credentials** handle token lifecycle automatically (request, refresh, inject)
- **Built-in pagination** loops through pages and combines results
- **Manual pagination** in Code nodes for complex cursor/offset patterns
- **Error handling** — retry on fail, check status codes, validate response shapes
- **Rate limit awareness** — read limit headers, back off proactively
- **Any API is connectable** — if it has HTTP endpoints, n8n can talk to it

FlagSmith changes now notify the product team within 5 minutes. No native integration needed — just HTTP requests with proper auth.

Next: Diana wants a weekly metrics report delivered every Monday at 9 AM. "Not 9:01. Not Sunday night. Monday. 9 AM. Eastern time." Scheduling sounds simple until time zones get involved.

---

[← Chapter 7: Database Operations](chapter-07-databases.md) | [Chapter 9: Scheduling →](chapter-09-scheduling.md)
