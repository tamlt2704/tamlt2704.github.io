# Chapter 9: Scheduling — Automated Reports

[← Chapter 8: API Integrations](chapter-08-apis.md) | [Chapter 10: Sub-Workflows →](chapter-10-sub-workflows.md)

---

## The Problem

Diana wants a weekly metrics report in #leadership every Monday at 9 AM Eastern:
- New signups this week
- Revenue from Stripe
- Support tickets opened/closed
- Deploy count

Currently, the intern compiles this manually every Monday morning. It takes 45 minutes and is always late because the intern forgets until someone asks.

You: "I'll schedule a workflow to run every Monday at 9 AM."

First attempt: you set the Schedule Trigger to Monday 9:00. The report fires at 9 AM UTC — which is 4 AM Eastern in winter and 5 AM Eastern in summer. Diana gets pinged before dawn.

Second attempt: you set it to 14:00 UTC (9 AM Eastern). It works until Daylight Saving Time shifts and the report arrives at 10 AM.

Time zones are the enemy of scheduled automation.

## Schedule Trigger: Configuration

The Schedule Trigger (formerly Cron) fires workflows on a time-based schedule.

### Basic Setup

1. Add a Schedule Trigger node
2. Configure the rule:

| Setting | Value |
|---|---|
| Trigger Interval | Weeks |
| Weeks Between Triggers | 1 |
| Trigger on Weekdays | Monday |
| Trigger at Hour | 9 |
| Trigger at Minute | 0 |

### Cron Expression (Advanced)

For complex schedules, use a cron expression:

```
┌───────── minute (0-59)
│ ┌─────── hour (0-23)
│ │ ┌───── day of month (1-31)
│ │ │ ┌─── month (1-12)
│ │ │ │ ┌─ day of week (0-7, 0=Sun)
│ │ │ │ │
0 9 * * 1    ← Every Monday at 9:00
0 */6 * * *  ← Every 6 hours
30 8 1 * *   ← 1st of every month at 8:30
0 9 * * 1-5  ← Weekdays at 9:00
```

## Time Zones: Getting It Right

n8n's Schedule Trigger supports time zones directly:

1. In the Schedule Trigger node, find **Timezone**
2. Set it to `America/New_York`

Now "9:00" means 9:00 AM Eastern — regardless of DST. n8n handles the UTC offset automatically.

**Critical**: If you don't set a timezone, the schedule uses the n8n server's timezone. If your server is UTC (common in Docker), your "9 AM" is 9 AM UTC.

### Common Time Zones

| Zone | Use For |
|---|---|
| `America/New_York` | US Eastern |
| `America/Chicago` | US Central |
| `America/Los_Angeles` | US Pacific |
| `Europe/London` | UK |
| `UTC` | When you explicitly want UTC |

## The Weekly Report Workflow

```json
{
  "name": "Weekly Metrics Report",
  "nodes": [
    {
      "parameters": {
        "rule": { "interval": [{ "field": "weeks", "weeksInterval": 1, "triggerAtDay": 1, "triggerAtHour": 9, "triggerAtMinute": 0 }] },
        "options": { "timezone": "America/New_York" }
      },
      "name": "Monday 9 AM ET",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT COUNT(*) as new_signups FROM customers WHERE created_at >= NOW() - INTERVAL '7 days'"
      },
      "name": "Get Signups",
      "type": "n8n-nodes-base.postgres",
      "position": [450, 200]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://api.stripe.com/v1/charges",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "stripeApi",
        "queryParameters": { "parameters": [{ "name": "created[gte]", "value": "={{ Math.floor((Date.now() - 7*24*60*60*1000) / 1000) }}" }] }
      },
      "name": "Get Stripe Revenue",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 350]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as opened, COUNT(*) FILTER (WHERE resolved_at >= NOW() - INTERVAL '7 days') as closed FROM support_tickets"
      },
      "name": "Get Tickets",
      "type": "n8n-nodes-base.postgres",
      "position": [450, 500]
    },
    {
      "parameters": { "mode": "combine", "combinationMode": "mergeByPosition" },
      "name": "Merge Results",
      "type": "n8n-nodes-base.merge",
      "position": [700, 350]
    },
    {
      "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": "const signups = $('Get Signups').first().json.new_signups;\nconst charges = $('Get Stripe Revenue').first().json.data || [];\nconst revenue = charges.reduce((sum, c) => sum + c.amount, 0) / 100;\nconst tickets = $('Get Tickets').first().json;\n\nconst weekStart = new Date(Date.now() - 7*24*60*60*1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });\nconst weekEnd = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' });\n\nreturn [{ json: {\n  message: `📊 *Weekly Report* (${weekStart} – ${weekEnd})\\n\\n• New signups: *${signups}*\\n• Revenue: *$${revenue.toLocaleString()}*\\n• Tickets opened: *${tickets.opened}* | closed: *${tickets.closed}*\\n• Net tickets: ${tickets.opened - tickets.closed > 0 ? '⚠️' : '✅'} ${tickets.opened - tickets.closed}`\n} }];"
      },
      "name": "Format Report",
      "type": "n8n-nodes-base.code",
      "position": [900, 350]
    },
    {
      "parameters": { "channel": "#leadership", "text": "={{ $json.message }}" },
      "name": "Post to Slack",
      "type": "n8n-nodes-base.slack",
      "position": [1100, 350]
    }
  ],
  "connections": {
    "Monday 9 AM ET": { "main": [[{ "node": "Get Signups", "type": "main", "index": 0 }, { "node": "Get Stripe Revenue", "type": "main", "index": 0 }, { "node": "Get Tickets", "type": "main", "index": 0 }]] },
    "Get Signups": { "main": [[{ "node": "Merge Results", "type": "main", "index": 0 }]] },
    "Get Stripe Revenue": { "main": [[{ "node": "Merge Results", "type": "main", "index": 0 }]] },
    "Get Tickets": { "main": [[{ "node": "Merge Results", "type": "main", "index": 0 }]] },
    "Merge Results": { "main": [[{ "node": "Format Report", "type": "main", "index": 0 }]] },
    "Format Report": { "main": [[{ "node": "Post to Slack", "type": "main", "index": 0 }]] }
  }
}
```

## Idempotency: Preventing Duplicate Reports

What if n8n restarts at 9:00 AM and the schedule fires twice? Or you manually test the workflow and it posts to #leadership?

### Pattern: Check If Already Ran Today

```javascript
// Code node — at the start of the workflow
const today = new Date().toISOString().split('T')[0]; // "2024-01-15"

// Check if we already posted today
const existing = await this.helpers.httpRequest({
  method: 'GET',
  url: `http://localhost:5432/...`, // or query your DB
});

// Alternative: use a simple file or DB flag
const lastRun = $('Check Last Run').first().json.last_run_date;

if (lastRun === today) {
  return []; // Already ran today — skip
}

return $input.all();
```

### Pattern: Execution Deduplication via Database

```sql
-- Before running the report
INSERT INTO workflow_runs (workflow_name, run_date, status)
VALUES ('weekly_report', CURRENT_DATE, 'started')
ON CONFLICT (workflow_name, run_date) DO NOTHING
RETURNING id;
```

If the INSERT returns nothing (conflict), the report already ran today. Skip it.

## Schedule Patterns

### Daily Digest (Weekdays Only)

```
Cron: 0 9 * * 1-5
Timezone: America/New_York
```

### Hourly During Business Hours

```
Cron: 0 9-17 * * 1-5
Timezone: America/New_York
```
Fires at 9:00, 10:00, ... 17:00, Monday through Friday.

### First of Month

```
Cron: 0 9 1 * *
Timezone: America/New_York
```

### Every 15 Minutes (Monitoring)

```
Trigger Interval: Minutes
Minutes Between Triggers: 15
```

No timezone needed for sub-hourly intervals — they're relative, not absolute.

## Handling Missed Executions

If n8n is down when a schedule should fire, the execution is missed. n8n does not "catch up" missed schedules by default.

For critical reports, add a safety net:

```
[Schedule: Monday 9 AM] → [Report Workflow]
[Schedule: Monday 9:30 AM] → [Check if report posted] → [IF not posted] → [Report Workflow]
```

The 9:30 check acts as a backup. If the 9 AM run succeeded, the check finds the report already posted and skips.

## What You Learned

- **Schedule Trigger** fires workflows on time-based intervals (cron or UI)
- **Timezone setting** is critical — always set it explicitly, never rely on server timezone
- **Cron expressions** for complex schedules (weekdays only, business hours, monthly)
- **Idempotency** prevents duplicate runs — check before executing
- **Missed executions** aren't retried automatically — build safety nets for critical schedules
- **Parallel data fetching** — trigger multiple data sources simultaneously, merge results

The weekly report now arrives at exactly 9:00 AM Eastern every Monday. No intern required. No DST bugs. Diana is happy.

But the report workflow is 8 nodes. The deploy notification is 6 nodes. The HubSpot sync is 7 nodes. And they all share the same "send Slack notification" pattern — channel, message, error handling. You've copy-pasted that Slack logic into 12 workflows. When you need to change the message format, you edit 12 workflows.

Time for modularity.

---

[← Chapter 8: API Integrations](chapter-08-apis.md) | [Chapter 10: Sub-Workflows →](chapter-10-sub-workflows.md)
