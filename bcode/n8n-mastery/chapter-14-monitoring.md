# Chapter 14: Monitoring & Observability

[← Chapter 13: Multi-Step Approvals](chapter-13-approvals.md) | [Chapter 15: Production Deployment →](chapter-15-production.md)

---

## The Problem

You have 15 active workflows. They process payments, sync contacts, classify tickets, send reports, and handle approvals. Everything works — until it doesn't.

Tuesday morning, Diana: "The weekly report didn't come yesterday. Was it Monday? I don't remember getting it."

You check. The Schedule Trigger fired. The Postgres query succeeded. The Stripe API call failed with a 401 — expired API key. The error handler caught it and... posted to #ops-alerts. Which nobody checks because it gets 200 messages a day from other tools.

The automation failed. The error handler worked. But nobody noticed the alert. The system is technically correct and practically useless.

Diana: "I need a dashboard. Green means working. Red means broken. I don't want to read Slack channels to know if my company's automation is healthy."

## Execution Logs: What n8n Gives You

n8n stores execution history by default. Access it via:
- **UI**: Click any workflow → "Executions" tab
- **API**: `GET /executions` endpoint

Each execution records:
- Start time, end time, duration
- Status (success, error, waiting)
- Input/output data for every node
- Error messages and stack traces

### Retention Settings

Configure in Settings → Workflow Settings:
- **Save successful executions**: Yes (for debugging)
- **Save failed executions**: Yes (always)
- **Execution data retention**: 30 days (balance storage vs. history)

For production, keep failed executions longer than successful ones.

## Health Check Workflow

Build a workflow that monitors your other workflows:

```json
{
  "name": "Monitor: Automation Health Check",
  "nodes": [
    {
      "parameters": {
        "rule": { "interval": [{ "field": "minutes", "minutesInterval": 15 }] }
      },
      "name": "Every 15 Minutes",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "http://localhost:5678/api/v1/executions",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "queryParameters": { "parameters": [
          { "name": "status", "value": "error" },
          { "name": "lastId", "value": "" },
          { "name": "limit", "value": "50" }
        ]}
      },
      "name": "Get Recent Failures",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    },
    {
      "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": "const executions = $input.first().json.data || [];\nconst fifteenMinAgo = Date.now() - 15 * 60 * 1000;\n\nconst recentFailures = executions.filter(e => \n  new Date(e.startedAt).getTime() > fifteenMinAgo\n);\n\nif (recentFailures.length === 0) {\n  return [{ json: { status: 'healthy', failures: 0 } }];\n}\n\nconst summary = recentFailures.map(e => \n  `• ${e.workflowData?.name || 'Unknown'}: ${e.stoppedAt ? 'failed' : 'running'}`\n).join('\\n');\n\nreturn [{ json: { status: 'degraded', failures: recentFailures.length, summary } }];"
      },
      "name": "Analyze",
      "type": "n8n-nodes-base.code",
      "position": [650, 300]
    },
    {
      "parameters": {
        "conditions": { "conditions": [{ "leftValue": "={{ $json.failures }}", "rightValue": "0", "operator": { "type": "number", "operation": "gt" } }] }
      },
      "name": "Any Failures?",
      "type": "n8n-nodes-base.if",
      "position": [850, 300]
    },
    {
      "parameters": {
        "channel": "#ops-critical",
        "text": "🔴 *Automation Health Alert*\n{{ $json.failures }} workflow(s) failed in the last 15 minutes:\n{{ $json.summary }}"
      },
      "name": "Alert Critical",
      "type": "n8n-nodes-base.slack",
      "position": [1050, 200]
    }
  ],
  "connections": {
    "Every 15 Minutes": { "main": [[{ "node": "Get Recent Failures", "type": "main", "index": 0 }]] },
    "Get Recent Failures": { "main": [[{ "node": "Analyze", "type": "main", "index": 0 }]] },
    "Analyze": { "main": [[{ "node": "Any Failures?", "type": "main", "index": 0 }]] },
    "Any Failures?": { "main": [[{ "node": "Alert Critical", "type": "main", "index": 0 }], []] }
  }
}
```

## Pattern: Heartbeat Monitoring

Some workflows should run on schedule. If they don't run, something is wrong. Monitor by checking "last successful execution" time.

```javascript
// Code node — check workflow heartbeats
const workflows = [
  { name: 'HubSpot Sync', expectedInterval: 24 * 60 * 60 * 1000 }, // daily
  { name: 'Weekly Report', expectedInterval: 7 * 24 * 60 * 60 * 1000 }, // weekly
  { name: 'Invoice Processing', expectedInterval: 60 * 60 * 1000 }, // hourly check
];

const results = [];

for (const wf of workflows) {
  const lastExecution = $('Get All Executions').all().find(
    e => e.json.workflowData?.name === wf.name && e.json.status === 'success'
  );
  
  const lastRun = lastExecution ? new Date(lastExecution.json.stoppedAt).getTime() : 0;
  const overdue = (Date.now() - lastRun) > wf.expectedInterval * 1.5; // 50% grace period
  
  results.push({
    json: {
      workflow: wf.name,
      lastRun: lastExecution ? lastExecution.json.stoppedAt : 'never',
      overdue,
      status: overdue ? '🔴' : '🟢'
    }
  });
}

return results;
```

## Alerting Strategy

Not all failures are equal. Route alerts by severity:

| Severity | Channel | Example |
|---|---|---|
| Critical | #ops-critical + PagerDuty | Payment processing down |
| Warning | #ops-alerts | HubSpot sync failed (will retry) |
| Info | #ops-log | Scheduled report completed |

### Alert Fatigue Prevention

The #ops-alerts channel with 200 messages/day is useless. Fix it:

1. **Deduplicate** — don't alert for the same failure every 15 minutes
2. **Aggregate** — "5 workflows failed" not 5 separate messages
3. **Escalate** — warning → critical if not resolved in 1 hour
4. **Resolve** — send "✅ Resolved" when the workflow succeeds again

```javascript
// Code node — deduplicate alerts
const currentFailures = $input.all().map(i => i.json.workflow);
const previousAlerts = $('Get Previous Alerts').all().map(i => i.json.workflow);

// Only alert for NEW failures (not already alerted)
const newFailures = currentFailures.filter(f => !previousAlerts.includes(f));

if (newFailures.length === 0) return []; // Nothing new to alert on

return newFailures.map(f => ({ json: { workflow: f, alertedAt: new Date().toISOString() } }));
```

## Metrics Dashboard

Build a daily metrics summary for Diana:

```javascript
// Code node — compile daily metrics
const executions = $('Get Today Executions').all();

const total = executions.length;
const successful = executions.filter(e => e.json.status === 'success').length;
const failed = executions.filter(e => e.json.status === 'error').length;
const successRate = total > 0 ? ((successful / total) * 100).toFixed(1) : 0;

const byWorkflow = {};
executions.forEach(e => {
  const name = e.json.workflowData?.name || 'Unknown';
  if (!byWorkflow[name]) byWorkflow[name] = { success: 0, error: 0 };
  byWorkflow[name][e.json.status === 'success' ? 'success' : 'error']++;
});

const report = Object.entries(byWorkflow)
  .map(([name, counts]) => `• ${name}: ${counts.success}✅ ${counts.error > 0 ? counts.error + '❌' : ''}`)
  .join('\n');

return [{ json: {
  message: `📊 *Daily Automation Report*\n\nTotal executions: ${total}\nSuccess rate: ${successRate}%\nFailed: ${failed}\n\n*By Workflow:*\n${report}`
} }];
```

## External Monitoring Integration

For production, integrate with external monitoring tools:

### Prometheus Metrics (via HTTP endpoint)

Create a workflow that exposes metrics at `/webhook/metrics`:

```javascript
// Code node — format as Prometheus metrics
const executions = $('Get Recent Executions').all();
const successful = executions.filter(e => e.json.status === 'success').length;
const failed = executions.filter(e => e.json.status === 'error').length;

const metrics = [
  `# HELP n8n_executions_total Total workflow executions`,
  `# TYPE n8n_executions_total counter`,
  `n8n_executions_total{status="success"} ${successful}`,
  `n8n_executions_total{status="error"} ${failed}`,
  `# HELP n8n_active_workflows Number of active workflows`,
  `# TYPE n8n_active_workflows gauge`,
  `n8n_active_workflows ${$('Get Active Workflows').all().length}`
].join('\n');

return [{ json: { metrics } }];
```

### Uptime Monitoring

Expose a simple health endpoint:

```
[Webhook: GET /health] → [Check DB Connection] → [Check Slack Connection] → [Respond: 200 OK]
```

Point UptimeRobot, Pingdom, or your monitoring tool at this endpoint. If it stops responding, n8n is down.

## What You Learned

- **Execution logs** record every run with full input/output data
- **Health check workflows** monitor other workflows on a schedule
- **Heartbeat monitoring** detects workflows that stopped running
- **Alert severity levels** route to appropriate channels (critical vs. info)
- **Alert fatigue prevention** — deduplicate, aggregate, escalate, resolve
- **Daily metrics** give leadership visibility into automation health
- **External integration** — expose Prometheus metrics or health endpoints
- **The meta-problem** — monitoring the monitors (keep health checks simple and independent)

Diana now has a daily report showing automation health. Critical failures page the on-call engineer. The #ops-critical channel gets 2-3 messages a week, not 200 a day. When something breaks, someone knows within 15 minutes.

But all of this runs on a single Docker container on your laptop. If your laptop sleeps, automation stops. If Docker crashes, everything is gone. You need production infrastructure.

---

[← Chapter 13: Multi-Step Approvals](chapter-13-approvals.md) | [Chapter 15: Production Deployment →](chapter-15-production.md)
