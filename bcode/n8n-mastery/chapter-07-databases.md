# Chapter 7: Database Operations — Beyond Spreadsheets

[← Chapter 6: Webhooks](chapter-06-webhooks.md) | [Chapter 8: API Integrations →](chapter-08-apis.md)

---

## The Problem

LaunchPad's customer data lives in a Google Sheet. It started as a quick hack — "just put it in the spreadsheet for now." That was 18 months ago. The sheet has 3,000 rows, loads in 8 seconds, and breaks when two people edit simultaneously.

Jake: "I need to look up a customer's plan tier when a support ticket comes in. The sheet takes forever and sometimes gives me stale data."

Aisha: "The HubSpot sync writes to the sheet, but if I'm editing at the same time, it overwrites my changes."

Diana: "We have a Postgres database. The engineering team uses it. Why are we still using spreadsheets for operational data?"

Good question. Time to move to a real database.

## Setting Up Postgres (Local Docker)

If you don't already have Postgres running:

```bash
docker run -d \
  --name launchpad-postgres \
  -e POSTGRES_USER=n8n \
  -e POSTGRES_PASSWORD=automation \
  -e POSTGRES_DB=launchpad \
  -p 5432:5432 \
  postgres:16
```

Create the customers table:

```sql
CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  company TEXT,
  plan_tier TEXT DEFAULT 'free',
  hubspot_id TEXT,
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_stripe ON customers(stripe_customer_id);
```

## Connecting n8n to Postgres

1. Go to Credentials → Add Credential → Postgres
2. Configure:
   - **Host**: `host.docker.internal` (if n8n is also in Docker) or `localhost`
   - **Port**: `5432`
   - **Database**: `launchpad`
   - **User**: `n8n`
   - **Password**: `automation`
3. Test connection → Save

## Basic Operations

### SELECT — Query Data

```json
{
  "parameters": {
    "operation": "select",
    "table": "customers",
    "where": {
      "values": [
        { "column": "email", "value": "={{ $json.customer_email }}" }
      ]
    },
    "limit": 1
  },
  "name": "Lookup Customer",
  "type": "n8n-nodes-base.postgres",
  "position": [450, 300]
}
```

Output:
```json
{ "id": 42, "email": "alice@acme.co", "name": "Alice", "plan_tier": "pro", "stripe_customer_id": "cus_abc123" }
```

### INSERT — Create Records

```json
{
  "parameters": {
    "operation": "insert",
    "table": "customers",
    "columns": {
      "mappingMode": "autoMapInputData"
    }
  },
  "name": "Insert Customer",
  "type": "n8n-nodes-base.postgres",
  "position": [450, 300]
}
```

Auto-map mode matches input field names to column names. If your input has `{ "email": "bob@co.com", "name": "Bob", "plan_tier": "free" }`, it inserts directly.

### UPSERT — Insert or Update

The most useful operation for syncs. If the record exists, update it. If not, create it.

```json
{
  "parameters": {
    "operation": "upsert",
    "table": "customers",
    "columns": {
      "mappingMode": "autoMapInputData"
    },
    "conflictColumns": ["email"]
  },
  "name": "Upsert Customer",
  "type": "n8n-nodes-base.postgres",
  "position": [450, 300]
}
```

**Conflict column** = the unique field to match on. If a row with that email exists, it updates. Otherwise, it inserts. No duplicates, no manual checking.

### Custom SQL — Execute Query

For complex queries, use raw SQL:

```json
{
  "parameters": {
    "operation": "executeQuery",
    "query": "SELECT c.email, c.plan_tier, COUNT(p.id) as payment_count FROM customers c LEFT JOIN payments p ON c.stripe_customer_id = p.customer_id WHERE c.plan_tier = $1 GROUP BY c.email, c.plan_tier ORDER BY payment_count DESC LIMIT $2",
    "options": {
      "queryParams": "={{ $json.tier }},={{ $json.limit }}"
    }
  },
  "name": "Custom Query",
  "type": "n8n-nodes-base.postgres",
  "position": [450, 300]
}
```

**Always use parameterized queries** (`$1`, `$2`) instead of string interpolation. This prevents SQL injection — especially important when query values come from webhooks or user input.

## The Sync Pattern: HubSpot → Postgres

Replace the Google Sheet with Postgres in the HubSpot sync:

```
[Schedule: Daily 6 AM] → [Get HubSpot Contacts] → [Transform] → [SplitInBatches] → [Upsert to Postgres] → [Wait] → (loop)
```

```javascript
// Code node — transform HubSpot contact to DB schema
const contact = $input.item.json;

return {
  json: {
    email: contact.properties.email,
    name: `${contact.properties.firstname || ''} ${contact.properties.lastname || ''}`.trim(),
    company: contact.properties.company || null,
    hubspot_id: contact.id,
    updated_at: new Date().toISOString()
  }
};
```

The upsert on `email` means running this sync daily is safe — existing records update, new records insert, nothing duplicates.

## Pattern: Lookup and Enrich

When a Stripe payment event arrives, look up the customer in Postgres to enrich the notification:

```
[Stripe Webhook] → [Verify] → [Lookup Customer by stripe_id] → [Format Message] → [Slack]
```

```
💰 *Payment received*: ${{ $json.amount / 100 }}
• Customer: {{ $('Lookup Customer').item.json.name }} ({{ $('Lookup Customer').item.json.plan_tier }})
• Email: {{ $('Lookup Customer').item.json.email }}
```

Now the Slack notification includes context from your database — not just the raw Stripe event.

## Pattern: Write-Back After Processing

After processing a support ticket, update the customer's record:

```javascript
// Update last_support_contact timestamp
{
  "operation": "executeQuery",
  "query": "UPDATE customers SET last_support_contact = NOW(), support_ticket_count = support_ticket_count + 1 WHERE email = $1",
  "options": { "queryParams": "={{ $json.customer_email }}" }
}
```

## Common Mistakes

### Not Handling Empty Results

A SELECT that matches nothing returns an empty array. Downstream nodes receive no items and don't execute. Add a check:

```javascript
// Code node after SELECT
const results = $input.all();
if (results.length === 0) {
  return [{ json: { found: false, email: $('Webhook').item.json.email } }];
}
return results.map(r => ({ json: { ...r.json, found: true } }));
```

### Inserting Duplicates

Without UPSERT, running a sync twice creates duplicate rows. Always use upsert for sync workflows, with the natural key (email, external ID) as the conflict column.

### Forgetting Timestamps

Always set `updated_at` on upserts. Without it, you can't tell when a record was last synced:

```sql
updated_at = NOW()  -- in your upsert
```

### Connection Limits

n8n opens a connection for each execution. If you have 20 workflows hitting Postgres simultaneously, you might exhaust the connection pool. Set `max_connections` appropriately in Postgres, or use connection pooling (PgBouncer) in production.

## What You Learned

- **Postgres node** supports SELECT, INSERT, UPDATE, DELETE, and UPSERT
- **UPSERT** is the sync workhorse — insert or update based on a conflict column
- **Parameterized queries** (`$1`, `$2`) prevent SQL injection
- **Auto-map mode** matches input fields to column names automatically
- **Lookup and enrich** — query the DB mid-workflow to add context
- **Always handle empty results** — SELECTs that match nothing produce no output items
- **Timestamps** — always track `updated_at` for sync workflows

The Google Sheet is retired. Customer data lives in Postgres. Queries are instant. Syncs don't conflict with manual edits. Jake can look up any customer in milliseconds.

Next problem: LaunchPad uses an internal tool for feature flags that has a REST API but no n8n integration. You need to connect to it anyway.

---

[← Chapter 6: Webhooks](chapter-06-webhooks.md) | [Chapter 8: API Integrations →](chapter-08-apis.md)
