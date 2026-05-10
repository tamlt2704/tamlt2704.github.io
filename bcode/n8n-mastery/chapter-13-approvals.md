# Chapter 13: Multi-Step Approvals — Human in the Loop

[← Chapter 12: File Processing](chapter-12-files.md) | [Chapter 14: Monitoring & Observability →](chapter-14-monitoring.md)

---

## The Problem

The invoice processing workflow from Chapter 12 works great — for small invoices. But LaunchPad's policy requires manager approval for any payment over $10,000. And refunds over $5,000 need both the support lead AND the finance lead to sign off.

Currently, someone sends a Slack message: "Hey Diana, can you approve this $15K invoice from CloudHost?" Diana replies "approved" three hours later. Someone else reads the reply and manually processes the payment. Sometimes the reply gets buried in Slack. Sometimes nobody follows up.

Diana: "I want a button. I click approve or reject. The system handles the rest. No chasing, no forgotten approvals."

## The Wait Node: Pausing for Humans

The **Wait** node pauses a workflow execution until an external event resumes it. The workflow stays "in progress" — holding its data in memory — until someone takes action.

### How It Works

1. Workflow reaches the Wait node
2. Execution pauses (data is preserved)
3. An external event resumes it (webhook callback, form submission, or timeout)
4. Workflow continues from where it paused

### Wait Node Options

| Resume On | Use Case |
|---|---|
| Webhook call | External system calls back |
| Form submission | Human fills out a form |
| Time interval | Auto-resume after delay |
| Specific date | Resume at a deadline |

## Pattern: Slack Approval with Buttons

### Step 1: Send Approval Request

Post a Slack message with action buttons using Block Kit:

```json
{
  "parameters": {
    "channel": "#approvals",
    "messageType": "block",
    "blocksUi": {
      "blocks": [
        {
          "type": "section",
          "text": { "type": "mrkdwn", "text": "🧾 *Approval Required*\n\nVendor: {{ $json.vendor }}\nAmount: ${{ $json.amount.toLocaleString() }}\nInvoice: {{ $json.invoice_number }}\nDue: {{ $json.due_date }}" }
        },
        {
          "type": "actions",
          "elements": [
            { "type": "button", "text": { "type": "plain_text", "text": "✅ Approve" }, "action_id": "approve", "value": "={{ $json.invoice_number }}", "style": "primary" },
            { "type": "button", "text": { "type": "plain_text", "text": "❌ Reject" }, "action_id": "reject", "value": "={{ $json.invoice_number }}", "style": "danger" }
          ]
        }
      ]
    }
  },
  "name": "Request Approval",
  "type": "n8n-nodes-base.slack",
  "position": [450, 300]
}
```

### Step 2: Wait for Response

```json
{
  "parameters": {
    "resume": "webhook",
    "options": {
      "timeout": "72",
      "timeoutUnit": "hours"
    }
  },
  "name": "Wait for Approval",
  "type": "n8n-nodes-base.wait",
  "position": [650, 300]
}
```

The Wait node generates a unique webhook URL. When Slack sends the button click to this URL, the workflow resumes.

### Step 3: Route the Decision

```
[Wait for Approval] → [IF: approved?]
    ├── true  → [Process Payment] → [Notify: Approved]
    └── false → [Notify: Rejected] → [Update Invoice Status]
```

## Form Trigger: Built-in Approval Forms

n8n has a **Form Trigger** node that creates a web form. Simpler than Slack buttons for some use cases.

### Creating an Approval Form

```json
{
  "parameters": {
    "formTitle": "Invoice Approval",
    "formDescription": "Review and approve or reject this invoice",
    "formFields": {
      "values": [
        { "fieldLabel": "Invoice", "fieldType": "text", "requiredField": true, "placeholder": "Auto-filled" },
        { "fieldLabel": "Amount", "fieldType": "text", "requiredField": true },
        { "fieldLabel": "Decision", "fieldType": "dropdown", "fieldOptions": { "values": [{ "option": "Approve" }, { "option": "Reject" }] } },
        { "fieldLabel": "Notes", "fieldType": "textarea", "requiredField": false }
      ]
    }
  },
  "name": "Approval Form",
  "type": "n8n-nodes-base.formTrigger",
  "position": [250, 300]
}
```

The form is accessible at a URL like: `http://localhost:5678/form/invoice-approval`

Send this URL in the approval request message. The approver clicks the link, fills the form, and the workflow continues.

## Timeout Handling

What if nobody approves? The invoice sits in limbo forever. Always handle timeouts.

### Wait Node Timeout

Set a timeout on the Wait node (e.g., 72 hours). When it expires, the workflow resumes with a timeout indicator:

```javascript
// Code node after Wait
const resumeData = $input.item.json;

if (resumeData.$resumeUrl === undefined && !resumeData.decision) {
  // Timeout — no response received
  return { json: { decision: 'timeout', reason: 'No response within 72 hours' } };
}

return $input.all();
```

### Escalation on Timeout

```
[Wait: 72h timeout] → [IF: timed out?]
    ├── true  → [Escalate to Diana's manager] → [Wait: 24h]
    └── false → [Process decision]
```

## Multi-Level Approvals

Refunds over $5,000 need two approvals: support lead AND finance lead.

### Sequential Approval

```
[Refund Request] → [Send to Support Lead] → [Wait] → [IF: approved?]
    ├── true  → [Send to Finance Lead] → [Wait] → [IF: approved?]
    │              ├── true  → [Process Refund]
    │              └── false → [Notify: Rejected by Finance]
    └── false → [Notify: Rejected by Support]
```

### Parallel Approval (Both Must Approve)

```
[Refund Request] → [Send to Support Lead] → [Wait] ─┐
                 → [Send to Finance Lead] → [Wait] ──┤
                                                      ↓
                                              [Merge Results] → [IF: both approved?]
```

Use the **Merge** node to combine both approval responses, then check if both said "approve."

## The Complete Approval Workflow

```json
{
  "name": "Invoice Approval Flow",
  "nodes": [
    {
      "parameters": { "httpMethod": "POST", "path": "invoice-approval-request" },
      "name": "Invoice Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "conditions": { "conditions": [{ "leftValue": "={{ $json.body.amount }}", "rightValue": "10000", "operator": { "type": "number", "operation": "gte" } }] }
      },
      "name": "Needs Approval?",
      "type": "n8n-nodes-base.if",
      "position": [450, 300]
    },
    {
      "parameters": {
        "channel": "#approvals",
        "text": "🧾 *Approval Needed*\nVendor: {{ $json.body.vendor }} | Amount: ${{ $json.body.amount }}\nInvoice: {{ $json.body.invoice_number }}\n\nApprove: {{ $resumeUrl }}?decision=approve\nReject: {{ $resumeUrl }}?decision=reject"
      },
      "name": "Request Approval",
      "type": "n8n-nodes-base.slack",
      "position": [650, 200]
    },
    {
      "parameters": {
        "resume": "webhook",
        "options": { "timeout": "72", "timeoutUnit": "hours" }
      },
      "name": "Wait for Decision",
      "type": "n8n-nodes-base.wait",
      "position": [850, 200]
    },
    {
      "parameters": {
        "conditions": { "conditions": [{ "leftValue": "={{ $json.query?.decision }}", "rightValue": "approve" }] }
      },
      "name": "Approved?",
      "type": "n8n-nodes-base.if",
      "position": [1050, 200]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "UPDATE invoices SET status = 'approved', approved_at = NOW() WHERE invoice_number = $1",
        "options": { "queryParams": "={{ $('Invoice Webhook').item.json.body.invoice_number }}" }
      },
      "name": "Mark Approved",
      "type": "n8n-nodes-base.postgres",
      "position": [1250, 100]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "UPDATE invoices SET status = 'rejected', rejected_at = NOW() WHERE invoice_number = $1",
        "options": { "queryParams": "={{ $('Invoice Webhook').item.json.body.invoice_number }}" }
      },
      "name": "Mark Rejected",
      "type": "n8n-nodes-base.postgres",
      "position": [1250, 300]
    }
  ],
  "connections": {
    "Invoice Webhook": { "main": [[{ "node": "Needs Approval?", "type": "main", "index": 0 }]] },
    "Needs Approval?": { "main": [[{ "node": "Request Approval", "type": "main", "index": 0 }], [{ "node": "Mark Approved", "type": "main", "index": 0 }]] },
    "Request Approval": { "main": [[{ "node": "Wait for Decision", "type": "main", "index": 0 }]] },
    "Wait for Decision": { "main": [[{ "node": "Approved?", "type": "main", "index": 0 }]] },
    "Approved?": { "main": [[{ "node": "Mark Approved", "type": "main", "index": 0 }], [{ "node": "Mark Rejected", "type": "main", "index": 0 }]] }
  }
}
```

## Common Pitfalls

### Execution Timeout vs. Wait Timeout

n8n has a global execution timeout (default: 60 minutes for self-hosted). If your Wait node waits 72 hours, you need to increase the execution timeout or use the **webhook resume** approach which persists across restarts.

Set in environment: `EXECUTIONS_TIMEOUT=-1` (no timeout) or `EXECUTIONS_TIMEOUT_MAX=259200` (72 hours in seconds).

### Lost State on Restart

If n8n restarts while a workflow is waiting, the execution may be lost. In production, enable **execution persistence** with a database backend (not SQLite). See Chapter 15.

### Duplicate Approvals

If someone clicks "Approve" twice, the Wait node only resumes once — the second click is ignored. But if you're using a separate webhook for approvals, add idempotency checks.

## What You Learned

- **Wait node** pauses execution until a human (or system) responds
- **Webhook resume** — the Wait node generates a unique URL that resumes the workflow
- **Form Trigger** creates web forms for structured human input
- **Timeout handling** — always set a timeout and handle the expiry case
- **Escalation** — if no response, escalate to the next level
- **Multi-level approvals** — sequential (one after another) or parallel (both must agree)
- **Execution persistence** — Wait nodes need database-backed executions to survive restarts

Diana now gets a clean approval request with one click to approve or reject. No Slack threads to chase. No forgotten invoices. Timeouts escalate automatically.

But now you have 15 active workflows. Some run every 5 minutes, some wait for webhooks, some wait for human approval. Diana asks the question that keeps every ops engineer up at night: "How do we know it's all still working?"

---

[← Chapter 12: File Processing](chapter-12-files.md) | [Chapter 14: Monitoring & Observability →](chapter-14-monitoring.md)
