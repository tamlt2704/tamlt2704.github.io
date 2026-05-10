# Chapter 0: Before You Start

[Chapter 1: Your First Workflow →](chapter-01-first-workflow.md)

---

## The Story

This is a series about n8n — but not the kind where you connect two nodes and call it automation.

You're an ops engineer at **LaunchPad**, a 40-person B2B SaaS startup growing faster than its processes can handle. The company uses Slack, Linear, Notion, HubSpot, Stripe, GitHub, and a Postgres database that holds everything together. Every tool has its own world. Nothing talks to anything else.

The result: people are the integration layer. The sales team manually copies leads from HubSpot to Notion. The support team manually creates Linear tickets from Intercom conversations. The finance team manually reconciles Stripe payments with invoices every Friday. The engineering team manually posts deploy notifications to Slack.

Your COO, **Diana**, pulls you into a room with a whiteboard covered in arrows:

"We're spending 30 hours a week on copy-paste between tools. That's almost a full-time employee doing nothing but being a human API. I need you to automate the boring stuff. All of it. You have n8n. Make it work."

You nod. You've seen workflow tools before. Drag some nodes, connect some lines. How hard can it be?

Over the next 15 chapters, you'll automate LaunchPad's operations from manual chaos to reliable, monitored, self-healing workflows. Every automation you build solves a real problem — syncing data, routing alerts, processing files, getting approvals. And every first attempt will break in a way that teaches you why production automation is harder than it looks.

The webhook will timeout. The loop will hit a rate limit. The error handler won't catch the error. The scheduled workflow will run twice because of a timezone bug. The sub-workflow will create an infinite loop. The AI node will hallucinate a customer name.

Each failure teaches you something about reliable automation that no drag-and-drop tutorial could.

By the end, you'll have a production-grade automation platform handling dozens of workflows — and you'll understand *when* to automate, *how* to make it reliable, and *what* to do when it breaks at 3 AM.

## How to Read This

Every chapter is the same loop:

1. Someone is doing something manually that's eating their week
2. You build the obvious automation
3. It works in testing but breaks in production
4. You learn the proper pattern
5. You implement it, monitor it, and move on

No concept shows up before you need it. You won't hear about error handling until a workflow fails silently and nobody notices for three days. You won't touch sub-workflows until your main workflow has 47 nodes and is impossible to debug.

The manual process comes first. The reliable automation follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Ops Engineer | "I'll just automate it." (Famous last words.) |
| **Diana** | COO | Pragmatic. "If it breaks, it's worse than manual." |
| **Jake** | Sales Lead | "I need leads in Notion within 5 minutes of signup." |
| **Aisha** | Support Lead | "Can the bot also check if they're a paying customer?" |
| **Dev Team** | Engineering | "Please don't break prod with your webhooks." |
| **The Intern** | Summer hire | Triggered the webhook 10,000 times testing with curl. |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | Deploy notifications are manual | Triggers, HTTP nodes, Slack integration |
| 2 | API responses need reshaping | Expressions, Code node, data transformation |
| 3 | Not all events need the same action | IF/Switch nodes, conditional routing |
| 4 | Bulk operations hit rate limits | Batching, loops, throttling |
| 5 | Workflow fails and nobody knows | Error triggers, retries, alerting |
| 6 | External services need to push data in | Webhooks, auth, request/response |
| 7 | Spreadsheets aren't scaling | Database nodes, queries, sync patterns |
| 8 | Tools don't have native integrations | HTTP Request, OAuth2, API pagination |
| 9 | Reports need to run on schedule | Cron, time zones, idempotent operations |
| 10 | Workflows are too complex to maintain | Sub-workflows, modularity, composition |
| 11 | Some decisions need intelligence | AI/LLM nodes, classification, extraction |
| 12 | Files arrive in various formats | File handling, parsing, cloud storage |
| 13 | Some actions need human approval | Wait nodes, forms, approval patterns |
| 14 | "Is the automation still running?" | Monitoring, health checks, observability |
| 15 | Local n8n isn't production-ready | Docker deployment, queue mode, scaling |

## Prerequisites

Two things: Docker and a willingness to break things.

### n8n (via Docker)

Don't install n8n globally. Use Docker — it's cleaner and matches how you'll run it in production:

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

Open http://localhost:5678. Create an account. You're in.

### Verify

You should see the n8n canvas — a blank workspace with a "+" button to add nodes. Click it, search for "Schedule Trigger," and drag it onto the canvas. If that works, you're ready.

### Alternative: n8n Cloud

If you don't want to self-host during learning, [n8n.cloud](https://n8n.cloud) offers a free tier. The UI is identical. The concepts transfer. We'll cover self-hosting in Chapter 15.

### Tools You'll Integrate With

Throughout the course, we'll connect to:

| Tool | Free Tier? | What We Use It For |
|---|---|---|
| Slack | Yes | Notifications, alerts |
| GitHub | Yes | Webhook triggers, issue creation |
| Postgres | Yes (local Docker) | Data storage, queries |
| HubSpot | Yes (free CRM) | Lead management |
| Stripe | Yes (test mode) | Payment events |
| OpenAI | Pay-per-use | AI classification (Ch 11) |

You don't need all of these on day one. Each chapter introduces the tools it needs.

### Quick Check

```bash
# n8n is running
curl -s http://localhost:5678/healthz
```

If you get a response, you're good.

## The Mental Model

n8n workflows are directed graphs:

```
[Trigger] → [Node A] → [Node B] → [Node C]
                ↓
            [Node D] → [Node E]
```

- **Triggers** start the workflow (schedule, webhook, event)
- **Nodes** do things (HTTP request, transform data, send message)
- **Connections** pass data between nodes
- **Expressions** reference data from previous nodes: `{{ $json.email }}`

Every node receives data from the previous node, does something with it, and passes the result forward. Data flows left to right. That's the whole model.

### Data Structure

Data in n8n flows as arrays of items. Each item is a JSON object:

```json
[
  { "json": { "name": "Alice", "email": "alice@example.com" } },
  { "json": { "name": "Bob", "email": "bob@example.com" } }
]
```

If a node receives 5 items, it typically processes all 5 and outputs 5 results. Some nodes (like IF) split items into different paths. Some nodes (like Merge) combine items from multiple paths.

Understanding this data flow is 80% of n8n mastery. The nodes themselves are straightforward — it's how data moves between them that trips people up.

## Workflow vs. Code

When should you use n8n vs. writing code?

| Use n8n When | Write Code When |
|---|---|
| Connecting existing tools | Building custom logic |
| Non-developers need to understand it | Performance is critical |
| The flow changes frequently | Complex data transformations |
| You need visual debugging | You need version control |
| Approval/human-in-the-loop steps | Sub-millisecond latency |

n8n isn't a replacement for code. It's a replacement for the glue scripts that connect your systems — the ones that live in a cron job nobody remembers, break silently, and have no monitoring.

Let's automate the first manual process.

---

[Chapter 1: Your First Workflow →](chapter-01-first-workflow.md)
